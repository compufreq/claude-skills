# Object Storage Reference

## Table of Contents
1. AWS S3
2. Azure Blob Storage
3. Security & Access Control
4. Lifecycle & Replication
5. Performance Optimization

---

## 1. AWS S3

### Production Bucket (Terraform)
```hcl
resource "aws_s3_bucket" "main" {
  bucket = "${var.project}-${var.environment}-assets"
  tags   = { Name = "${var.project}-${var.environment}-assets" }
}

resource "aws_s3_bucket_versioning" "main" {
  bucket = aws_s3_bucket.main.id
  versioning_configuration { status = "Enabled" }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "main" {
  bucket = aws_s3_bucket.main.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.s3.arn
    }
    bucket_key_enabled = true
  }
}

resource "aws_s3_bucket_public_access_block" "main" {
  bucket                  = aws_s3_bucket.main.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_logging" "main" {
  bucket        = aws_s3_bucket.main.id
  target_bucket = aws_s3_bucket.logs.id
  target_prefix = "s3-access-logs/"
}

# Lifecycle rules
resource "aws_s3_bucket_lifecycle_configuration" "main" {
  bucket = aws_s3_bucket.main.id

  rule {
    id     = "transition-to-ia"
    status = "Enabled"
    transition {
      days          = 30
      storage_class = "STANDARD_IA"
    }
    transition {
      days          = 90
      storage_class = "GLACIER_IR"
    }
    transition {
      days          = 365
      storage_class = "DEEP_ARCHIVE"
    }
    noncurrent_version_expiration {
      noncurrent_days = 30
    }
  }

  rule {
    id     = "abort-multipart"
    status = "Enabled"
    abort_incomplete_multipart_upload {
      days_after_initiation = 7
    }
  }
}

# Cross-region replication
resource "aws_s3_bucket_replication_configuration" "main" {
  count  = var.environment == "production" ? 1 : 0
  bucket = aws_s3_bucket.main.id
  role   = aws_iam_role.replication.arn

  rule {
    id     = "replicate-all"
    status = "Enabled"
    destination {
      bucket        = aws_s3_bucket.replica.arn
      storage_class = "STANDARD_IA"
      encryption_configuration {
        replica_kms_key_id = aws_kms_key.s3_replica.arn
      }
    }
    source_selection_criteria {
      sse_kms_encrypted_objects { status = "Enabled" }
    }
  }
}

# CORS (for web uploads)
resource "aws_s3_bucket_cors_configuration" "main" {
  bucket = aws_s3_bucket.main.id
  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["GET", "PUT", "POST"]
    allowed_origins = ["https://app.example.com"]
    expose_headers  = ["ETag"]
    max_age_seconds = 3600
  }
}
```

### Presigned URLs (Application Code)
```python
import boto3
s3 = boto3.client('s3')

# Generate upload URL (PUT)
upload_url = s3.generate_presigned_url('put_object',
    Params={'Bucket': 'my-bucket', 'Key': 'uploads/file.pdf', 'ContentType': 'application/pdf'},
    ExpiresIn=3600)

# Generate download URL (GET)
download_url = s3.generate_presigned_url('get_object',
    Params={'Bucket': 'my-bucket', 'Key': 'uploads/file.pdf'},
    ExpiresIn=3600)
```

---

## 2. Azure Blob Storage

### Production Storage Account (Terraform)
```hcl
resource "azurerm_storage_account" "main" {
  name                     = "${replace(var.project, "-", "")}${var.environment}"
  resource_group_name      = azurerm_resource_group.main.name
  location                 = azurerm_resource_group.main.location
  account_tier             = "Standard"
  account_replication_type = var.environment == "production" ? "GRS" : "LRS"
  account_kind             = "StorageV2"
  min_tls_version          = "TLS1_2"
  enable_https_traffic_only = true

  blob_properties {
    versioning_enabled  = true
    change_feed_enabled = true
    delete_retention_policy { days = 30 }
    container_delete_retention_policy { days = 30 }
  }

  network_rules {
    default_action             = "Deny"
    bypass                     = ["AzureServices"]
    virtual_network_subnet_ids = [azurerm_subnet.app.id]
  }

  identity { type = "SystemAssigned" }

  tags = {
    Environment = var.environment
    Project     = var.project
  }
}

resource "azurerm_storage_container" "assets" {
  name                  = "assets"
  storage_account_name  = azurerm_storage_account.main.name
  container_access_type = "private"
}

# Lifecycle management
resource "azurerm_storage_management_policy" "main" {
  storage_account_id = azurerm_storage_account.main.id

  rule {
    name    = "transition-and-delete"
    enabled = true
    filters {
      blob_types   = ["blockBlob"]
      prefix_match = ["assets/"]
    }
    actions {
      base_blob {
        tier_to_cool_after_days_since_modification_greater_than    = 30
        tier_to_archive_after_days_since_modification_greater_than = 90
        delete_after_days_since_modification_greater_than          = 365
      }
      snapshot {
        delete_after_days_since_creation_greater_than = 30
      }
      version {
        delete_after_days_since_creation = 30
      }
    }
  }
}
```

---

## 3. Security & Access Control

### S3 Bucket Policy (Least Privilege)
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowAppRole",
      "Effect": "Allow",
      "Principal": { "AWS": "arn:aws:iam::123456789:role/app-role" },
      "Action": ["s3:GetObject", "s3:PutObject"],
      "Resource": "arn:aws:s3:::my-bucket/uploads/*"
    },
    {
      "Sid": "DenyUnencryptedUploads",
      "Effect": "Deny",
      "Principal": "*",
      "Action": "s3:PutObject",
      "Resource": "arn:aws:s3:::my-bucket/*",
      "Condition": {
        "StringNotEquals": { "s3:x-amz-server-side-encryption": "aws:kms" }
      }
    },
    {
      "Sid": "EnforceTLS",
      "Effect": "Deny",
      "Principal": "*",
      "Action": "s3:*",
      "Resource": ["arn:aws:s3:::my-bucket", "arn:aws:s3:::my-bucket/*"],
      "Condition": { "Bool": { "aws:SecureTransport": "false" } }
    }
  ]
}
```

---

## 4. Performance Optimization

### S3 Performance
- **Multipart upload** for files > 100MB (parallel parts)
- **S3 Transfer Acceleration** for cross-region uploads
- **CloudFront** for read-heavy workloads (cache at edge)
- **Prefix distribution** — S3 partitions by prefix; spread keys evenly
- **S3 Select** — query CSV/JSON/Parquet without downloading entire object

### Azure Blob Performance
- **Premium tier** for latency-sensitive workloads (SSD-backed)
- **Azure CDN / Front Door** for read caching
- **Block blob tiers** — Hot/Cool/Archive based on access patterns
- **AzCopy** for high-performance bulk transfers



---
