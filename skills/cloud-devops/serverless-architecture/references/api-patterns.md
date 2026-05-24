# API Patterns Reference

## Table of Contents
1. REST API Architecture
2. GraphQL (AppSync)
3. WebSocket APIs
4. API Security
5. API Patterns Comparison

---

## 1. REST API Architecture

### AWS: API Gateway + Lambda
```
Client → API Gateway (HTTP API) → Lambda → DynamoDB
              │                       │
         Auth (JWT/Cognito)     Business Logic
         Rate Limiting          Data Access
         Request Validation     Response Formatting
         CORS                   Error Handling
```

### Terraform: API Gateway HTTP API + Lambda
```hcl
# API Gateway
resource "aws_apigatewayv2_api" "main" {
  name          = "${var.project}-api"
  protocol_type = "HTTP"
  cors_configuration {
    allow_origins = var.cors_origins
    allow_methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    allow_headers = ["Content-Type", "Authorization"]
    max_age       = 3600
  }
}

resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.main.id
  name        = "$default"
  auto_deploy = true
  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.apigw.arn
    format = jsonencode({
      requestId = "$context.requestId"
      ip        = "$context.identity.sourceIp"
      method    = "$context.httpMethod"
      path      = "$context.path"
      status    = "$context.status"
      latency   = "$context.responseLatency"
      error     = "$context.error.message"
    })
  }
  default_route_settings {
    throttling_burst_limit = 1000
    throttling_rate_limit  = 500
  }
}

# JWT Authorizer (Cognito / Auth0)
resource "aws_apigatewayv2_authorizer" "jwt" {
  api_id           = aws_apigatewayv2_api.main.id
  authorizer_type  = "JWT"
  identity_sources = ["$request.header.Authorization"]
  name             = "jwt-auth"
  jwt_configuration {
    audience = [var.auth_audience]
    issuer   = var.auth_issuer
  }
}

# Routes
resource "aws_apigatewayv2_route" "get_users" {
  api_id             = aws_apigatewayv2_api.main.id
  route_key          = "GET /users"
  target             = "integrations/${aws_apigatewayv2_integration.users.id}"
  authorization_type = "JWT"
  authorizer_id      = aws_apigatewayv2_authorizer.jwt.id
}

resource "aws_apigatewayv2_route" "create_user" {
  api_id             = aws_apigatewayv2_api.main.id
  route_key          = "POST /users"
  target             = "integrations/${aws_apigatewayv2_integration.users.id}"
  authorization_type = "JWT"
  authorizer_id      = aws_apigatewayv2_authorizer.jwt.id
}

# Lambda integration
resource "aws_apigatewayv2_integration" "users" {
  api_id                 = aws_apigatewayv2_api.main.id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.users.invoke_arn
  payload_format_version = "2.0"
}
```

### Lambda Handler Pattern
```javascript
// Single-purpose handler
export const handler = async (event) => {
  try {
    const { httpMethod, pathParameters, body, requestContext } = event;
    const userId = requestContext.authorizer?.jwt?.claims?.sub;

    switch (`${httpMethod} ${event.routeKey?.split(' ')[1] || ''}`) {
      case 'GET /users':
        return await listUsers(event.queryStringParameters);
      case 'GET /users/{id}':
        return await getUser(pathParameters.id, userId);
      case 'POST /users':
        return await createUser(JSON.parse(body), userId);
      case 'PUT /users/{id}':
        return await updateUser(pathParameters.id, JSON.parse(body), userId);
      default:
        return { statusCode: 404, body: JSON.stringify({ error: 'Not found' }) };
    }
  } catch (error) {
    console.error(JSON.stringify({ level: 'error', error: error.message, stack: error.stack }));
    return { statusCode: error.statusCode || 500, body: JSON.stringify({ error: error.message }) };
  }
};
```

### Azure: API Management + Functions
```hcl
resource "azurerm_api_management" "main" {
  name                = "${var.project}-apim"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  publisher_name      = var.publisher_name
  publisher_email     = var.publisher_email
  sku_name            = var.environment == "production" ? "Standard_1" : "Consumption_0"

  identity { type = "SystemAssigned" }
}

resource "azurerm_api_management_api" "users" {
  name                = "users-api"
  resource_group_name = azurerm_resource_group.main.name
  api_management_name = azurerm_api_management.main.name
  revision            = "1"
  display_name        = "Users API"
  path                = "users"
  protocols           = ["https"]
  service_url         = "https://${azurerm_linux_function_app.main.default_hostname}/api"
}
```

---

## 2. GraphQL (AWS AppSync)

```hcl
resource "aws_appsync_graphql_api" "main" {
  name                = "${var.project}-api"
  authentication_type = "AMAZON_COGNITO_USER_POOLS"
  schema              = file("schema.graphql")

  user_pool_config {
    user_pool_id   = aws_cognito_user_pool.main.id
    default_action = "ALLOW"
    aws_region     = var.region
  }

  log_config {
    cloudwatch_logs_role_arn = aws_iam_role.appsync_logs.arn
    field_log_level          = "ERROR"
  }

  xray_enabled = true
}

# DynamoDB data source
resource "aws_appsync_datasource" "users" {
  api_id           = aws_appsync_graphql_api.main.id
  name             = "UsersTable"
  type             = "AMAZON_DYNAMODB"
  service_role_arn = aws_iam_role.appsync.arn
  dynamodb_config {
    table_name = aws_dynamodb_table.users.name
    region     = var.region
  }
}

# Lambda data source (for complex resolvers)
resource "aws_appsync_datasource" "complex" {
  api_id           = aws_appsync_graphql_api.main.id
  name             = "ComplexResolver"
  type             = "AWS_LAMBDA"
  service_role_arn = aws_iam_role.appsync.arn
  lambda_config {
    function_arn = aws_lambda_function.resolver.arn
  }
}
```

### GraphQL Schema
```graphql
type User {
  id: ID!
  name: String!
  email: String!
  orders: [Order!]!
}

type Order {
  id: ID!
  total: Float!
  status: OrderStatus!
  createdAt: AWSDateTime!
}

enum OrderStatus { PENDING CONFIRMED SHIPPED DELIVERED }

type Query {
  getUser(id: ID!): User
  listUsers(limit: Int, nextToken: String): UserConnection!
}

type Mutation {
  createUser(input: CreateUserInput!): User!
  updateUser(id: ID!, input: UpdateUserInput!): User!
}

type UserConnection {
  items: [User!]!
  nextToken: String
}

input CreateUserInput { name: String!, email: String! }
input UpdateUserInput { name: String, email: String }
```

---

## 3. WebSocket APIs

### AWS API Gateway WebSocket
```hcl
resource "aws_apigatewayv2_api" "websocket" {
  name                       = "${var.project}-ws"
  protocol_type              = "WEBSOCKET"
  route_selection_expression = "$request.body.action"
}

resource "aws_apigatewayv2_route" "connect" {
  api_id    = aws_apigatewayv2_api.websocket.id
  route_key = "$connect"
  target    = "integrations/${aws_apigatewayv2_integration.connect.id}"
}

resource "aws_apigatewayv2_route" "disconnect" {
  api_id    = aws_apigatewayv2_api.websocket.id
  route_key = "$disconnect"
  target    = "integrations/${aws_apigatewayv2_integration.disconnect.id}"
}

resource "aws_apigatewayv2_route" "message" {
  api_id    = aws_apigatewayv2_api.websocket.id
  route_key = "sendMessage"
  target    = "integrations/${aws_apigatewayv2_integration.message.id}"
}
```

### Connection Management Pattern
```javascript
// Store connections in DynamoDB
const { DynamoDBClient, PutItemCommand, DeleteItemCommand } = require('@aws-sdk/client-dynamodb');
const db = new DynamoDBClient({});

// $connect handler
exports.connect = async (event) => {
  await db.send(new PutItemCommand({
    TableName: process.env.CONNECTIONS_TABLE,
    Item: {
      connectionId: { S: event.requestContext.connectionId },
      userId: { S: event.requestContext.authorizer?.userId || 'anonymous' },
      connectedAt: { N: String(Date.now()) },
    },
  }));
  return { statusCode: 200 };
};

// $disconnect handler
exports.disconnect = async (event) => {
  await db.send(new DeleteItemCommand({
    TableName: process.env.CONNECTIONS_TABLE,
    Key: { connectionId: { S: event.requestContext.connectionId } },
  }));
  return { statusCode: 200 };
};
```

---

## 4. API Security

### Security Layers

| Layer | Mechanism | AWS | Azure |
|-------|----------|-----|-------|
| Authentication | JWT / OAuth2 | Cognito + JWT Authorizer | Azure AD + APIM policy |
| Authorization | Claims / RBAC | Lambda Authorizer | APIM policy |
| Rate limiting | Per-client throttling | Usage plans + API keys | APIM rate-limit policy |
| Input validation | Schema validation | API Gateway models | APIM validate-content policy |
| WAF | OWASP rule protection | AWS WAF on API Gateway | Azure WAF on Front Door |

### Lambda Authorizer (Custom Auth)
```javascript
exports.handler = async (event) => {
  const token = event.authorizationToken?.replace('Bearer ', '');
  const decoded = await verifyToken(token); // Your JWT verification

  return {
    principalId: decoded.sub,
    policyDocument: {
      Version: '2012-10-17',
      Statement: [{
        Action: 'execute-api:Invoke',
        Effect: decoded ? 'Allow' : 'Deny',
        Resource: event.methodArn,
      }],
    },
    context: {
      userId: decoded.sub,
      role: decoded.role,
    },
  };
};
```

---

## 5. API Patterns Comparison

| Pattern | When | AWS | Azure |
|---------|------|-----|-------|
| REST (HTTP) | Standard CRUD APIs | API Gateway HTTP API | APIM + Functions |
| REST (Regional) | Full API management | API Gateway REST API | APIM Standard |
| GraphQL | Flexible queries, mobile | AppSync | Functions + Hot Chocolate |
| WebSocket | Real-time, chat, notifications | API Gateway WebSocket | SignalR + Functions |
| gRPC | Service-to-service, high perf | ALB + ECS (not Lambda) | AKS (not Functions) |

### REST vs GraphQL Decision

| Factor | REST | GraphQL |
|--------|------|---------|
| Mobile clients | Multiple endpoints, over-fetching | Single endpoint, client picks fields |
| Caching | HTTP caching (easy) | Complex (query-level) |
| File uploads | Native | Requires workaround |
| Real-time | Polling or WebSocket | Subscriptions (AppSync) |
| Learning curve | Low | Medium |
| Best for | Simple CRUD, public APIs | Mobile apps, flexible queries |



---
