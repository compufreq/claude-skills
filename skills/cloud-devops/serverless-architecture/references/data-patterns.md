# Serverless Data Patterns Reference

## Table of Contents
1. DynamoDB Single-Table Design
2. S3 Event Processing
3. Stream Processing
4. CQRS with Serverless
5. Data Pipeline Patterns

---

## 1. DynamoDB Single-Table Design

### Design Process
```
1. List access patterns (all queries the app needs)
2. Design primary key (PK + SK) to satisfy most patterns
3. Add GSIs for remaining access patterns
4. Use overloaded keys for multi-entity tables
```

### Example: E-Commerce

**Access Patterns:**
1. Get user by ID
2. Get user's orders (sorted by date)
3. Get order by ID
4. Get order items
5. Get orders by status
6. Get user's addresses

**Table Design:**
```
PK                  | SK                    | GSI1PK              | GSI1SK           | Data
--------------------|----------------------|---------------------|------------------|------
USER#usr_123        | PROFILE              |                     |                  | name, email
USER#usr_123        | ADDR#addr_1          |                     |                  | street, city
USER#usr_123        | ORDER#2025-01-15#001 | STATUS#pending      | ORDER#2025-01-15 | total
ORDER#ord_001       | META                 | USER#usr_123        | ORDER#2025-01-15 | total, status
ORDER#ord_001       | ITEM#sku_abc         |                     |                  | qty, price
ORDER#ord_001       | ITEM#sku_def         |                     |                  | qty, price
```

**Queries:**
```javascript
// 1. Get user profile
const user = await docClient.get({ TableName, Key: { PK: 'USER#123', SK: 'PROFILE' } });

// 2. Get user's orders (newest first)
const orders = await docClient.query({
  TableName,
  KeyConditionExpression: 'PK = :pk AND begins_with(SK, :sk)',
  ExpressionAttributeValues: { ':pk': 'USER#123', ':sk': 'ORDER#' },
  ScanIndexForward: false,
  Limit: 20,
});

// 3. Get order with items
const orderData = await docClient.query({
  TableName,
  KeyConditionExpression: 'PK = :pk',
  ExpressionAttributeValues: { ':pk': 'ORDER#ord_001' },
});

// 5. Get orders by status (GSI1)
const pending = await docClient.query({
  TableName, IndexName: 'GSI1',
  KeyConditionExpression: 'GSI1PK = :pk',
  ExpressionAttributeValues: { ':pk': 'STATUS#pending' },
});
```

---

## 2. S3 Event Processing

### File Upload Processing
```
User uploads file → S3 bucket → S3 Event → Lambda
                                              ↓
                                    Process (resize, validate, scan)
                                              ↓
                                    Store result (DynamoDB, another S3)
                                              ↓
                                    Notify (SNS, EventBridge)
```

### Terraform
```hcl
resource "aws_s3_bucket_notification" "uploads" {
  bucket = aws_s3_bucket.uploads.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.process_upload.arn
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = "uploads/"
    filter_suffix       = ".pdf"
  }

  lambda_function {
    lambda_function_arn = aws_lambda_function.process_image.arn
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = "images/"
  }
}

resource "aws_lambda_permission" "s3" {
  statement_id  = "AllowS3"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.process_upload.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.uploads.arn
}
```

### Image Processing Lambda
```javascript
const { S3Client, GetObjectCommand, PutObjectCommand } = require('@aws-sdk/client-s3');
const sharp = require('sharp');

const s3 = new S3Client({});

exports.handler = async (event) => {
  for (const record of event.Records) {
    const bucket = record.s3.bucket.name;
    const key = decodeURIComponent(record.s3.object.key);

    // Get original image
    const { Body } = await s3.send(new GetObjectCommand({ Bucket: bucket, Key: key }));
    const buffer = Buffer.from(await Body.transformToByteArray());

    // Generate thumbnails
    const sizes = [
      { name: 'thumb', width: 150, height: 150 },
      { name: 'medium', width: 600, height: 600 },
      { name: 'large', width: 1200, height: 1200 },
    ];

    for (const size of sizes) {
      const resized = await sharp(buffer)
        .resize(size.width, size.height, { fit: 'inside' })
        .webp({ quality: 80 })
        .toBuffer();

      await s3.send(new PutObjectCommand({
        Bucket: process.env.OUTPUT_BUCKET,
        Key: `${size.name}/${key.replace(/\.[^.]+$/, '.webp')}`,
        Body: resized,
        ContentType: 'image/webp',
      }));
    }
  }
};
```

---

## 3. Stream Processing

### DynamoDB Streams → Lambda
```
DynamoDB write → Stream record → Lambda
                                   ↓
                    Update search index (OpenSearch)
                    Publish event (EventBridge)
                    Update materialized view
                    Audit log
```

```hcl
resource "aws_lambda_event_source_mapping" "streams" {
  event_source_arn  = aws_dynamodb_table.orders.stream_arn
  function_name     = aws_lambda_function.stream_processor.arn
  starting_position = "LATEST"
  batch_size        = 100

  maximum_batching_window_in_seconds = 5
  maximum_retry_attempts             = 3
  bisect_batch_on_function_error     = true
  parallelization_factor             = 10

  destination_config {
    on_failure {
      destination_arn = aws_sqs_queue.stream_dlq.arn
    }
  }

  filter_criteria {
    filter {
      pattern = jsonencode({
        eventName = ["INSERT", "MODIFY"]
        dynamodb = {
          NewImage = {
            entityType = { S = ["ORDER"] }
          }
        }
      })
    }
  }
}
```

### Stream Processor
```javascript
exports.handler = async (event) => {
  for (const record of event.Records) {
    const { eventName, dynamodb } = record;
    const newImage = AWS.DynamoDB.Converter.unmarshall(dynamodb.NewImage || {});
    const oldImage = AWS.DynamoDB.Converter.unmarshall(dynamodb.OldImage || {});

    switch (eventName) {
      case 'INSERT':
        await indexInOpenSearch(newImage);
        await publishEvent('order.created', newImage);
        break;
      case 'MODIFY':
        if (newImage.status !== oldImage.status) {
          await publishEvent('order.status.changed', {
            orderId: newImage.orderId,
            oldStatus: oldImage.status,
            newStatus: newImage.status,
          });
        }
        await updateSearchIndex(newImage);
        break;
    }
  }
};
```

---

## 4. CQRS with Serverless

### Architecture
```
Write Path:
  API Gateway → Lambda → DynamoDB → Stream → Lambda → Read Model
                              ↓
                         EventBridge → Analytics, Notifications

Read Path:
  API Gateway → Lambda → Read Model (DynamoDB / OpenSearch / ElastiCache)
```

### Implementation
```
Write Model (DynamoDB):
  PK: ORDER#ord_001, SK: EVENT#2025-01-15T10:30:00Z
  Event: OrderPlaced { orderId, userId, items, total }
  
  PK: ORDER#ord_001, SK: EVENT#2025-01-15T10:35:00Z
  Event: PaymentProcessed { orderId, paymentId, amount }

Read Model (DynamoDB or ElastiCache):
  PK: ORDER#ord_001
  { orderId, userId, items, total, status, paymentId, ... }
  (Materialized from events by stream processor)
```

### Benefits
- Write model captures events (audit trail, replay)
- Read model optimized for queries (denormalized, pre-computed)
- Independent scaling of reads vs writes
- Can rebuild read model by replaying events

---

## 5. Data Pipeline Patterns

### ETL with Step Functions
```
Schedule (EventBridge)
  → Step Functions
    → Extract (Lambda: query API / read S3)
    → Transform (Lambda: clean, enrich, validate)
    → Load (Lambda: write to database / data warehouse)
    → Notify (SNS: success/failure)
```

### Real-Time Analytics Pipeline
```
API → Lambda → DynamoDB
                 ↓ (Stream)
              Lambda → Kinesis Data Firehose → S3 (data lake)
                                                 ↓
                                              Athena (query)
                                              QuickSight (dashboard)
```

### File Processing Pipeline
```
S3 Upload → EventBridge → Step Functions
  ↓
  ├── Validate (Lambda: file type, size, malware scan)
  ├── Process (Lambda: parse CSV, extract data)
  ├── Enrich (Lambda: lookup additional data)
  ├── Store (Lambda: write to DynamoDB)
  └── Notify (SNS: processing complete)
  
  On error at any step:
  └── Compensate → Move file to error bucket → Alert team
```



---
