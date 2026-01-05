# Bitbucket Configuration

## Authentication

**Credentials are stored separately for security.**

This file contains non-sensitive configuration only. For credential setup, see `.credentials.example`.

### Recommended Setup

1. Copy the credentials template:
   ```bash
   cp bitbucket-repo-lookup/references/.credentials.example bitbucket-repo-lookup/references/.credentials
   ```

2. Edit `.credentials` with your actual Bitbucket credentials

3. Source the credentials file before running scripts:
   ```bash
   source bitbucket-repo-lookup/references/.credentials
   ```

### Alternative Methods

**Environment Variables (Cross-session)**
```bash
# Add to your ~/.bashrc or ~/.zshrc
export BITBUCKET_USERNAME="your-username"
export BITBUCKET_APP_PASSWORD="your-app-password"
```

**CLI Arguments (One-time use)**
```bash
python bitbucket-repo-lookup/scripts/bitbucket_api.py list --workspace WORKSPACE --username USER --password PASS
```

See `SKILL.md` for complete authentication documentation.

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
