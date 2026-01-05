# Bitbucket Configuration

## Authentication

Configure your Bitbucket credentials below. **Do not commit this file with real credentials.**

### Option 1: App Password (Recommended)

Create an app password in Bitbucket:
1. Go to **Personal settings** → **App passwords**
2. Click **Create app password**
3. Give it a label (e.g., "claude-code-skill")
4. Select permissions:
   - `Repositories: Read` (required)
   - `Repositories: Write` (only if you need to push)
5. Copy the generated password

```yaml
auth:
  method: app_password
  username: your-bitbucket-username
  app_password: your-app-password-here
```

### Option 2: Access Token

For workspace-level access or CI/CD integration:

```yaml
auth:
  method: access_token
  token: your-access-token-here
```

### Option 3: Environment Variables

For security, you can use environment variables instead of hardcoding:

```yaml
auth:
  method: env
  username_var: BITBUCKET_USERNAME
  password_var: BITBUCKET_APP_PASSWORD
```

Then set in your shell:
```bash
export BITBUCKET_USERNAME="your-username"
export BITBUCKET_APP_PASSWORD="your-app-password"
```

---

## Workspace Configuration

```yaml
workspace:
  # Your Bitbucket workspace slug (from URL: bitbucket.org/WORKSPACE/repo)
  slug: your-workspace-slug

  # Optional: Default project to filter (leave empty for all projects)
  default_project: ""
```

---

## Clone Settings

```yaml
clone:
  # Default directory for cloned repositories
  base_directory: ~/repos

  # Clone method: ssh or https
  method: https

  # SSH host (only used if method is ssh)
  ssh_host: bitbucket.org

  # Create subdirectories by project
  organize_by_project: true

  # Clone depth (0 for full history, or number for shallow clone)
  depth: 0
```

### Directory Structure Examples

With `organize_by_project: true`:
```
~/repos/
├── backend/
│   ├── user-service/
│   └── payment-gateway/
├── frontend/
│   └── web-dashboard/
└── mobile/
    └── mobile-app/
```

With `organize_by_project: false`:
```
~/repos/
├── user-service/
├── payment-gateway/
├── web-dashboard/
└── mobile-app/
```

---

## API Settings

```yaml
api:
  # Bitbucket API base URL (usually don't change this)
  base_url: https://api.bitbucket.org/2.0

  # Request timeout in seconds
  timeout: 30

  # Number of repositories per page (max 100)
  page_size: 50

  # Maximum pages to fetch (0 for unlimited)
  max_pages: 0

  # Retry failed requests
  retry_count: 3
  retry_delay: 2
```

---

## Filtering Defaults

```yaml
filters:
  # Default language filter (empty for all)
  language: ""

  # Only show repos updated within N days (0 for no filter)
  updated_within_days: 0

  # Exclude archived repositories
  exclude_archived: true

  # Exclude forks
  exclude_forks: false
```

---

## Output Preferences

```yaml
output:
  # Show full repository details in listing
  verbose: false

  # Date format for display
  date_format: "%Y-%m-%d"

  # Show clone progress
  show_progress: true

  # Confirm before cloning multiple repositories
  confirm_bulk_clone: true

  # Maximum repos to clone without confirmation
  bulk_clone_threshold: 5
```

---

## Example Complete Configuration

```yaml
auth:
  method: app_password
  username: jsmith
  app_password: ATBBxxxxxxxxxxxxxxxxxx

workspace:
  slug: acme-corp
  default_project: ""

clone:
  base_directory: ~/projects/acme
  method: https
  organize_by_project: true
  depth: 0

api:
  base_url: https://api.bitbucket.org/2.0
  timeout: 30
  page_size: 50
  max_pages: 0
  retry_count: 3
  retry_delay: 2

filters:
  language: ""
  updated_within_days: 0
  exclude_archived: true
  exclude_forks: false

output:
  verbose: false
  date_format: "%Y-%m-%d"
  show_progress: true
  confirm_bulk_clone: true
  bulk_clone_threshold: 5
```

---

## Quick Setup Checklist

- [ ] Created Bitbucket app password with repository read access
- [ ] Set username and app_password in auth section
- [ ] Set workspace slug
- [ ] Set preferred clone base_directory
- [ ] Choose clone method (https or ssh)
- [ ] Added this file to `.gitignore` if sharing the skill
