# Bitbucket API Guide

Reference for the Bitbucket Cloud REST API v2.0 used by this skill.

## Authentication

### App Password Authentication

Most common method for personal use:

```bash
curl -u username:app_password \
  https://api.bitbucket.org/2.0/repositories/{workspace}
```

### Bearer Token Authentication

For OAuth2 access tokens:

```bash
curl -H "Authorization: Bearer {access_token}" \
  https://api.bitbucket.org/2.0/repositories/{workspace}
```

---

## Core Endpoints

### List Repositories in Workspace

```
GET https://api.bitbucket.org/2.0/repositories/{workspace}
```

**Parameters:**
| Parameter | Type   | Description                              |
|-----------|--------|------------------------------------------|
| page      | int    | Page number (starts at 1)                |
| pagelen   | int    | Results per page (max 100, default 10)   |
| sort      | string | Sort field (e.g., `-updated_on`)         |
| q         | string | Query filter (see Query Language below)  |

**Example Response:**
```json
{
  "pagelen": 10,
  "size": 42,
  "values": [
    {
      "type": "repository",
      "uuid": "{repository-uuid}",
      "name": "user-service",
      "full_name": "acme-corp/user-service",
      "slug": "user-service",
      "description": "User management microservice",
      "language": "python",
      "created_on": "2023-06-15T10:30:00.000000+00:00",
      "updated_on": "2024-01-15T14:22:00.000000+00:00",
      "size": 47185920,
      "is_private": true,
      "project": {
        "key": "BACKEND",
        "name": "Backend Services"
      },
      "mainbranch": {
        "name": "main",
        "type": "branch"
      },
      "links": {
        "clone": [
          {
            "href": "https://bitbucket.org/acme-corp/user-service.git",
            "name": "https"
          },
          {
            "href": "git@bitbucket.org:acme-corp/user-service.git",
            "name": "ssh"
          }
        ],
        "html": {
          "href": "https://bitbucket.org/acme-corp/user-service"
        }
      }
    }
  ],
  "page": 1,
  "next": "https://api.bitbucket.org/2.0/repositories/acme-corp?page=2"
}
```

### Get Single Repository

```
GET https://api.bitbucket.org/2.0/repositories/{workspace}/{repo_slug}
```

### List Commits

```
GET https://api.bitbucket.org/2.0/repositories/{workspace}/{repo_slug}/commits
```

**Get latest commit:**
```
GET https://api.bitbucket.org/2.0/repositories/{workspace}/{repo_slug}/commits?pagelen=1
```

---

## Query Language

Bitbucket supports a powerful query language for filtering repositories.

### Syntax

```
q=field operator "value"
```

### Operators

| Operator | Description              | Example                           |
|----------|--------------------------|-----------------------------------|
| =        | Equals                   | `project.key = "BACKEND"`         |
| !=       | Not equals               | `language != "java"`              |
| ~        | Contains (fuzzy match)   | `name ~ "service"`                |
| >        | Greater than             | `updated_on > 2024-01-01`         |
| <        | Less than                | `size < 1000000`                  |
| >=       | Greater or equal         | `created_on >= 2023-01-01`        |
| <=       | Less or equal            | `updated_on <= 2024-12-31`        |

### Logical Operators

Combine conditions with `AND` and `OR`:

```
q=project.key = "BACKEND" AND language = "python"
q=name ~ "api" OR name ~ "service"
```

### Common Filters

**By project:**
```
q=project.key = "BACKEND"
```

**By language:**
```
q=language = "python"
```

**By name (contains):**
```
q=name ~ "service"
```

**Recently updated:**
```
q=updated_on > 2024-01-01
```

**Combined example:**
```
q=project.key = "BACKEND" AND language = "python" AND updated_on > 2024-01-01
```

### Sortable Fields

| Field       | Description                    | Example           |
|-------------|--------------------------------|-------------------|
| name        | Repository name (alphabetical) | `sort=name`       |
| updated_on  | Last update timestamp          | `sort=-updated_on`|
| created_on  | Creation timestamp             | `sort=-created_on`|
| size        | Repository size                | `sort=-size`      |

Use `-` prefix for descending order.

---

## Pagination

Bitbucket uses cursor-based pagination:

1. First request returns `next` URL if more pages exist
2. Follow `next` URL for subsequent pages
3. Stop when `next` is not present

**Example pagination flow:**
```python
url = f"{base_url}/repositories/{workspace}"
all_repos = []

while url:
    response = requests.get(url, auth=(user, password))
    data = response.json()
    all_repos.extend(data['values'])
    url = data.get('next')  # None when no more pages
```

---

## Rate Limiting

Bitbucket Cloud has rate limits:

| Limit Type      | Authenticated | Unauthenticated |
|-----------------|---------------|-----------------|
| Requests/hour   | 1000          | 60              |
| Concurrent      | 10            | 3               |

**Rate limit headers:**
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 950
X-RateLimit-Reset: 1705350000
```

**Handling 429 responses:**
```python
if response.status_code == 429:
    retry_after = int(response.headers.get('Retry-After', 60))
    time.sleep(retry_after)
    # Retry request
```

---

## Error Responses

### Common Errors

| Status | Error                  | Cause                          |
|--------|------------------------|--------------------------------|
| 401    | Unauthorized           | Invalid or missing credentials |
| 403    | Forbidden              | No access to resource          |
| 404    | Not Found              | Workspace/repo doesn't exist   |
| 429    | Too Many Requests      | Rate limit exceeded            |
| 500    | Internal Server Error  | Bitbucket server issue         |

### Error Response Format

```json
{
  "type": "error",
  "error": {
    "message": "Repository not found",
    "detail": "The repository acme-corp/unknown-repo does not exist."
  }
}
```

---

## Clone URLs

Each repository provides clone URLs in the response:

```json
"links": {
  "clone": [
    {
      "href": "https://bitbucket.org/acme-corp/user-service.git",
      "name": "https"
    },
    {
      "href": "git@bitbucket.org:acme-corp/user-service.git",
      "name": "ssh"
    }
  ]
}
```

### HTTPS Clone

Requires username and app password:
```bash
git clone https://username:app_password@bitbucket.org/workspace/repo.git
```

Or with credential helper:
```bash
git clone https://bitbucket.org/workspace/repo.git
# Git will prompt for credentials
```

### SSH Clone

Requires SSH key configured in Bitbucket:
```bash
git clone git@bitbucket.org:workspace/repo.git
```

---

## Useful API Calls

### Count Repositories

```bash
# Returns size field with total count
curl -u user:pass "https://api.bitbucket.org/2.0/repositories/{workspace}?pagelen=1" \
  | jq '.size'
```

### List Projects in Workspace

```
GET https://api.bitbucket.org/2.0/workspaces/{workspace}/projects
```

### Get Repository Branches

```
GET https://api.bitbucket.org/2.0/repositories/{workspace}/{repo_slug}/refs/branches
```

### Check Permissions

```
GET https://api.bitbucket.org/2.0/user/permissions/repositories?q=repository.full_name="{workspace}/{repo}"
```

---

## API Request Examples

### Python (requests)

```python
import requests

auth = ('username', 'app_password')
base_url = 'https://api.bitbucket.org/2.0'

# List repos
response = requests.get(
    f'{base_url}/repositories/acme-corp',
    auth=auth,
    params={'pagelen': 50, 'sort': '-updated_on'}
)
repos = response.json()['values']
```

### cURL

```bash
# List all repos
curl -u username:app_password \
  "https://api.bitbucket.org/2.0/repositories/acme-corp?pagelen=50"

# Filter by project
curl -u username:app_password \
  "https://api.bitbucket.org/2.0/repositories/acme-corp?q=project.key%3D%22BACKEND%22"

# Search by name
curl -u username:app_password \
  "https://api.bitbucket.org/2.0/repositories/acme-corp?q=name~%22service%22"
```

---

## Best Practices

1. **Always use authentication** — Higher rate limits and access to private repos
2. **Request only needed fields** — Use `fields` parameter to reduce payload
3. **Use pagination** — Never assume all results fit in one response
4. **Cache when possible** — Repository metadata doesn't change often
5. **Handle rate limits gracefully** — Implement exponential backoff
6. **Validate workspace access** — Check permissions before bulk operations
