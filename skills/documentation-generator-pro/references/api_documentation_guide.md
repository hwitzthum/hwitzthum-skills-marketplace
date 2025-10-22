# Complete API Documentation Guide

Comprehensive guide for creating professional, user-friendly API documentation.

## Table of Contents

- [Overview](#overview)
- [Documentation Structure](#documentation-structure)
- [Writing Style](#writing-style)
- [API Reference Format](#api-reference-format)
- [Code Examples](#code-examples)
- [Error Documentation](#error-documentation)
- [Authentication & Security](#authentication--security)
- [Best Practices](#best-practices)
- [Tools and Automation](#tools-and-automation)

## Overview

Good API documentation is essential for developer adoption and success. It should be:

- **Complete** - Cover all endpoints, parameters, and responses
- **Accurate** - Tested and verified examples
- **Clear** - Easy to understand for target audience
- **Discoverable** - Well-organized and searchable
- **Maintainable** - Easy to keep up-to-date

### Documentation Audience

Consider these user types:

1. **First-time users** - Need quick start and basic examples
2. **Integration developers** - Need complete reference and edge cases
3. **Troubleshooters** - Need error codes and debugging info
4. **Decision makers** - Need capabilities overview and pricing

## Documentation Structure

### Essential Sections

Every API documentation should include:

```markdown
1. Overview & Introduction
   - What the API does
   - Key features and benefits
   - Use cases

2. Getting Started
   - Quick start guide (< 5 minutes to first success)
   - Authentication setup
   - First API call

3. Authentication
   - How to authenticate
   - Getting credentials
   - Token management

4. API Reference
   - All endpoints with examples
   - Request/response formats
   - Parameters and types

5. Error Handling
   - Error codes and meanings
   - Common errors and solutions
   - Retry logic

6. Rate Limits & Quotas
   - Request limits
   - Headers to monitor
   - Handling rate limits

7. SDKs & Libraries
   - Official SDKs
   - Community libraries
   - Code examples

8. Changelog
   - Version history
   - Breaking changes
   - Migration guides
```

### Recommended File Structure

```
docs/
├── README.md                    # Overview and quick start
├── getting-started.md           # Detailed getting started
├── authentication.md            # Auth details
├── api-reference/
│   ├── overview.md             # API overview
│   ├── users.md                # Users endpoints
│   ├── products.md             # Products endpoints
│   └── webhooks.md             # Webhooks
├── guides/
│   ├── pagination.md           # How to handle pagination
│   ├── filtering.md            # Filtering and search
│   ├── rate-limiting.md        # Rate limit handling
│   └── webhooks.md             # Setting up webhooks
├── errors.md                    # Error reference
├── sdks.md                      # SDK documentation
└── changelog.md                 # Version history
```

## Writing Style

### Voice and Perspective

**Use second person ("you"):**

```markdown
✅ Good: You can authenticate using a Bearer token
❌ Bad: Users can authenticate using a Bearer token
```

**Use active voice:**

```markdown
✅ Good: The API returns a JSON response
❌ Bad: A JSON response is returned by the API
```

**Be conversational but professional:**

```markdown
✅ Good: Let's create your first API request
❌ Bad: The subsequent procedural execution initiates...
```

### Clarity and Conciseness

**Be specific with values:**

```markdown
✅ Good: Set timeout to 30 seconds
❌ Bad: Set an appropriate timeout value
```

**Use examples liberally:**

```markdown
✅ Good:
The `filter` parameter accepts field:value pairs.

Example: `filter=status:active`

❌ Bad:
The filter parameter accepts various filtering criteria.
```

**Explain the "why" when necessary:**

```markdown
✅ Good:
Use exponential backoff when retrying failed requests. This prevents
overwhelming the server during outages and improves your success rate.

❌ Bad:
Implement retry logic with exponential backoff.
```

## API Reference Format

### Endpoint Documentation Template

```markdown
### GET /api/v1/resource

Brief one-line description of what this endpoint does.

**Authentication:** Required

**Rate Limit:** 100 requests per minute

#### Request

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | Resource unique identifier |

**Query Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `include` | string | No | null | Related resources to include |
| `fields` | string | No | all | Comma-separated fields to return |

**Headers:**

| Header | Required | Description |
|--------|----------|-------------|
| `Authorization` | Yes | Bearer token |
| `Content-Type` | Yes | Must be `application/json` |

#### Response

**Success Response (200 OK):**

```json
{
  "id": "res_123abc",
  "name": "Example Resource",
  "status": "active",
  "created_at": "2024-01-15T10:30:00Z"
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique identifier |
| `name` | string | Resource name |
| `status` | enum | One of: `active`, `inactive`, `pending` |
| `created_at` | string (ISO 8601) | Creation timestamp |

#### Error Responses

**401 Unauthorized:**
```json
{
  "error": {
    "code": "unauthorized",
    "message": "Invalid or expired token"
  }
}
```

**404 Not Found:**
```json
{
  "error": {
    "code": "not_found",
    "message": "Resource not found"
  }
}
```

#### Example Request

```bash
curl -X GET "https://api.example.com/v1/resource/res_123abc?include=metadata" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json"
```

#### Example Response

```json
{
  "id": "res_123abc",
  "name": "Example Resource",
  "status": "active",
  "metadata": {
    "created_by": "user_456",
    "tags": ["important", "featured"]
  },
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-16T14:20:00Z"
}
```

#### SDKs

**Python:**
```python
resource = client.resources.get('res_123abc', include='metadata')
```

**JavaScript:**
```javascript
const resource = await client.resources.get('res_123abc', {
  include: 'metadata'
});
```

#### Notes

- The `include` parameter supports: `metadata`, `relations`, `stats`
- Maximum 100 resources can be retrieved per request
- Soft-deleted resources return 404
```

### Data Types Documentation

Document all custom data types:

```markdown
## Data Types

### Resource Object

```json
{
  "id": "string",
  "name": "string",
  "status": "enum",
  "metadata": "object",
  "created_at": "string (ISO 8601)"
}
```

**Fields:**

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `id` | string | Unique identifier | Read-only |
| `name` | string | Display name | 1-255 characters |
| `status` | enum | Current status | `active`, `inactive`, `pending` |
| `metadata` | object | Custom key-value pairs | Max 50 keys |
| `created_at` | timestamp | Creation time | ISO 8601 format |
```

### Enumerations

Document all enum values:

```markdown
### Status Enum

| Value | Description | Transitions |
|-------|-------------|-------------|
| `active` | Resource is active | Can transition to `inactive` |
| `inactive` | Resource is disabled | Can transition to `active` |
| `pending` | Awaiting activation | Auto-transitions to `active` after 24h |
| `deleted` | Soft-deleted | Cannot transition, permanent |
```

## Code Examples

### Example Quality Standards

**All code examples must:**

1. **Be complete and runnable**
   ```python
   ✅ Good:
   import requests

   response = requests.get(
       'https://api.example.com/resource',
       headers={'Authorization': 'Bearer TOKEN'}
   )
   print(response.json())

   ❌ Bad:
   response = api.get('resource')
   ```

2. **Use realistic data**
   ```javascript
   ✅ Good:
   const user = {
     email: 'sarah.connor@example.com',
     name: 'Sarah Connor',
     role: 'admin'
   };

   ❌ Bad:
   const user = {
     email: 'test@test.com',
     name: 'Test User',
     role: 'test'
   };
   ```

3. **Handle errors**
   ```python
   ✅ Good:
   try:
       response = client.create_resource(data)
   except RateLimitError:
       time.sleep(60)
       response = client.create_resource(data)
   except APIError as e:
       print(f"Error: {e.message}")

   ❌ Bad:
   response = client.create_resource(data)
   ```

4. **Include expected output**
   ```markdown
   ✅ Good:
   ```python
   result = client.get_user('user_123')
   print(result)
   ```

   **Output:**
   ```json
   {
     "id": "user_123",
     "name": "John Doe"
   }
   ```
   ```

### Multi-Language Examples

Provide examples in popular languages:

```markdown
### Creating a Resource

**Python:**
```python
import requests

response = requests.post(
    'https://api.example.com/v1/resources',
    headers={
        'Authorization': 'Bearer YOUR_API_KEY',
        'Content-Type': 'application/json'
    },
    json={
        'name': 'New Resource',
        'status': 'active'
    }
)

resource = response.json()
print(f"Created: {resource['id']}")
```

**JavaScript (Node.js):**
```javascript
const axios = require('axios');

const response = await axios.post(
  'https://api.example.com/v1/resources',
  {
    name: 'New Resource',
    status: 'active'
  },
  {
    headers: {
      'Authorization': 'Bearer YOUR_API_KEY',
      'Content-Type': 'application/json'
    }
  }
);

console.log(`Created: ${response.data.id}`);
```

**cURL:**
```bash
curl -X POST 'https://api.example.com/v1/resources' \
  -H 'Authorization: Bearer YOUR_API_KEY' \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "New Resource",
    "status": "active"
  }'
```
```

## Error Documentation

### Error Response Format

Document your error format consistently:

```markdown
## Error Responses

All errors follow this format:

```json
{
  "error": {
    "code": "error_code",
    "message": "Human-readable error message",
    "details": {
      "field": "Additional context"
    },
    "request_id": "req_xyz789"
  }
}
```

### Error Codes Reference

| Status | Code | Description | Action |
|--------|------|-------------|--------|
| 400 | `bad_request` | Invalid request format | Check request syntax |
| 400 | `validation_error` | Field validation failed | See `details` field |
| 401 | `unauthorized` | Missing/invalid auth | Check API key |
| 403 | `forbidden` | Insufficient permissions | Upgrade plan or contact support |
| 404 | `not_found` | Resource doesn't exist | Verify resource ID |
| 409 | `conflict` | Resource state conflict | Check resource status |
| 429 | `rate_limit_exceeded` | Too many requests | Wait and retry with backoff |
| 500 | `internal_error` | Server error | Retry later or contact support |
| 503 | `service_unavailable` | Temporary outage | Retry with backoff |
```

### Error Handling Examples

```markdown
### Handling Rate Limits

**Python with exponential backoff:**
```python
import time
import requests

def make_request_with_retry(url, max_retries=3):
    for attempt in range(max_retries):
        response = requests.get(url)

        if response.status_code == 429:
            # Rate limited
            retry_after = int(response.headers.get('Retry-After', 60))
            time.sleep(retry_after)
            continue

        return response

    raise Exception('Max retries exceeded')
```

**JavaScript with exponential backoff:**
```javascript
async function makeRequestWithRetry(url, maxRetries = 3) {
  for (let attempt = 0; attempt < maxRetries; attempt++) {
    const response = await fetch(url);

    if (response.status === 429) {
      const retryAfter = response.headers.get('Retry-After') || 60;
      await new Promise(resolve => setTimeout(resolve, retryAfter * 1000));
      continue;
    }

    return response;
  }

  throw new Error('Max retries exceeded');
}
```
```

## Authentication & Security

### Authentication Documentation

```markdown
## Authentication

### Getting an API Key

1. Sign up at [platform.example.com](https://platform.example.com)
2. Navigate to Settings > API Keys
3. Click "Generate New API Key"
4. Copy your key immediately (it won't be shown again)

⚠️ **Security Warning:** Never commit API keys to version control or share them publicly.

### Authentication Methods

#### Bearer Token (Recommended)

```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
  https://api.example.com/v1/resource
```

#### API Key Header

```bash
curl -H "X-API-Key: YOUR_API_KEY" \
  https://api.example.com/v1/resource
```

### Token Management

**Token Lifecycle:**
- Tokens don't expire by default
- Can be revoked at any time
- Create multiple tokens for different applications

**Best Practices:**
1. Use environment variables for API keys
2. Rotate keys regularly (every 90 days)
3. Use different keys for development and production
4. Revoke compromised keys immediately

### Scopes and Permissions

API keys can have different permission scopes:

| Scope | Permissions | Use Case |
|-------|-------------|----------|
| `read` | Read-only access | Analytics, reporting |
| `write` | Read and write | Integration apps |
| `admin` | Full access | Management tools |
```

## Best Practices

### 1. Interactive Documentation

Provide interactive API explorers:

- **Swagger/OpenAPI** - Auto-generate interactive docs
- **Postman Collections** - Shareable API collections
- **API Playground** - In-browser testing

### 2. Versioning Strategy

```markdown
## API Versioning

**Current Version:** v1

**Version Format:** `/v{major}/endpoint`

**Example:** `https://api.example.com/v1/resources`

### Version Policy

- **Major versions** - Breaking changes
- **Minor versions** - Backward-compatible features
- **Patch versions** - Bug fixes

### Deprecation Process

1. **Announce** - 90 days notice before deprecation
2. **Warning headers** - Add deprecation headers to responses
3. **Support** - Old version supported for 12 months
4. **Sunset** - Remove old version

**Migration guides** provided for all major versions.
```

### 3. Performance Documentation

Document performance characteristics:

```markdown
## Performance Guidelines

### Response Times

| Endpoint Type | Target (p95) | Max (p99) |
|---------------|--------------|-----------|
| Read (GET) | < 200ms | < 500ms |
| Write (POST/PUT) | < 500ms | < 1s |
| Batch operations | < 2s | < 5s |

### Rate Limits

- **Default:** 1000 requests/hour per API key
- **Burst:** Up to 100 requests/minute
- **Enterprise:** Custom limits available

**Headers:**
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640995200
```

### Pagination

Use `limit` and `offset` for large datasets:

```http
GET /v1/resources?limit=100&offset=200
```

**Limits:**
- Min: 1
- Max: 100
- Default: 20
```

### 4. Webhooks Documentation

If your API supports webhooks:

```markdown
## Webhooks

Receive real-time notifications about events.

### Setting Up Webhooks

1. Create webhook endpoint (HTTPS required)
2. Register endpoint in dashboard
3. Verify endpoint ownership
4. Subscribe to events

### Webhook Events

| Event | Trigger | Payload |
|-------|---------|---------|
| `resource.created` | New resource created | Full resource object |
| `resource.updated` | Resource modified | Updated fields only |
| `resource.deleted` | Resource deleted | Resource ID |

### Webhook Payload

```json
{
  "event": "resource.created",
  "timestamp": "2024-01-15T10:30:00Z",
  "data": {
    "id": "res_123",
    "name": "New Resource"
  },
  "signature": "sha256=..."
}
```

### Verifying Webhooks

**Python:**
```python
import hmac
import hashlib

def verify_webhook(payload, signature, secret):
    expected = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(f'sha256={expected}', signature)
```

### Retry Logic

Failed webhooks are retried:
- Attempt 1: Immediate
- Attempt 2: After 1 minute
- Attempt 3: After 5 minutes
- Attempt 4: After 30 minutes
- Attempt 5: After 2 hours

After 5 failures, webhook is disabled.
```

## Tools and Automation

### Documentation Tools

1. **OpenAPI/Swagger**
   - Generate from code
   - Interactive UI
   - Client generation

2. **Postman**
   - API collections
   - Automated testing
   - Collaboration

3. **ReadMe.io**
   - Hosted documentation
   - API explorer
   - Analytics

4. **Docusaurus**
   - Static site generator
   - Version control
   - Search

### Automation

**Auto-generate from code:**

```python
# Example: FastAPI automatically generates OpenAPI docs
from fastapi import FastAPI

app = FastAPI(
    title="My API",
    description="API documentation",
    version="1.0.0"
)

@app.get("/resource/{id}")
def get_resource(id: str):
    """
    Get a resource by ID.

    Args:
        id: Resource identifier

    Returns:
        Resource object
    """
    pass
```

**Testing examples:**

```python
# Ensure all code examples work
import doctest

def test_documentation_examples():
    """Test all code examples in docs"""
    doctest.testfile("docs/api-reference.md")
```

## Maintenance and Updates

### Documentation Lifecycle

1. **Write** - Document alongside code
2. **Review** - Technical and copy review
3. **Publish** - Make available to users
4. **Monitor** - Track usage and feedback
5. **Update** - Keep in sync with changes

### Keeping Docs Updated

- **CI/CD integration** - Build docs on every release
- **Version warnings** - Flag outdated content
- **User feedback** - "Was this helpful?" buttons
- **Analytics** - Track popular pages and search terms

### Quality Checklist

- [ ] All endpoints documented
- [ ] All parameters explained
- [ ] Examples tested and working
- [ ] Error codes documented
- [ ] Authentication covered
- [ ] Rate limits specified
- [ ] SDKs referenced
- [ ] Changelog updated
- [ ] No broken links
- [ ] Code examples syntax-highlighted

---

**See Also:**
- [Documentation Standards](./documentation_standards.md)
- [Diagram Best Practices](./diagram_best_practices.md)