---
name: bitbucket-repo-lookup
description: "Look up, list, and clone repositories from Bitbucket workspaces. Use when you need to explore available repositories, search by name/project, or download specific repos to your local machine."
---

# Bitbucket Repository Lookup

## Core Philosophy

This skill bridges the gap between your Bitbucket cloud workspace and your local development environment. Instead of manually browsing Bitbucket's web interface, use this skill to:

- **Discover** repositories across your workspaces
- **Search** by repository name, project, or language
- **Preview** repository details before downloading
- **Clone** one, many, or all repositories with a single command

## Workflow: Query to Clone

```
┌─────────────────────────────────────────────────────────────────────────┐
│  1. AUTHENTICATE     │  2. LIST/SEARCH    │  3. SELECT    │  4. CLONE  │
├─────────────────────────────────────────────────────────────────────────┤
│  Set credentials     │  Query workspace   │  User picks   │  Download  │
│  in config.md        │  repos with        │  from list    │  to local  │
│                      │  optional filters  │  or "all"     │  directory │
└─────────────────────────────────────────────────────────────────────────┘
```

## Dependencies

| Skill | Path | Purpose |
|-------|------|---------|
| credential-setup | `credential-setup/SKILL.md` | Configure Bitbucket API credentials |

## Workflow

### 1. Configure Credentials
- Read credential-setup skill
- Ensure `.credentials` exists with BITBUCKET_USERNAME and BITBUCKET_APP_PASSWORD
- Alternative: Set environment variables or use CLI args (see config.md)

### 2. Configure Workspace
- Edit `references/config.md` to set workspace slug and clone preferences

### 3. List Repositories
- Use natural language queries to list and filter repositories:
  - "List all repositories in my Bitbucket workspace"
  - "Show me repos in the 'backend' project"
  - "Find repositories containing 'api' in the name"

### 4. Select and Clone
- Specify repositories to clone by number, name, or "all":
  - "Clone repos 1, 3, and 5"
  - "Download all of them"
  - "Just clone the 'user-service' repository"

## Listing Repositories

When you request a repository listing, Claude will display:

```
┌──────────────────────────────────────────────────────────────────────────┐
│ # │ Repository Name      │ Project    │ Language   │ Updated            │
├──────────────────────────────────────────────────────────────────────────┤
│ 1 │ user-service         │ backend    │ Python     │ 2024-01-15         │
│ 2 │ payment-gateway      │ backend    │ Go         │ 2024-01-14         │
│ 3 │ web-dashboard        │ frontend   │ TypeScript │ 2024-01-13         │
│ 4 │ mobile-app           │ mobile     │ Kotlin     │ 2024-01-12         │
│ 5 │ shared-utils         │ libraries  │ Python     │ 2024-01-10         │
└──────────────────────────────────────────────────────────────────────────┘

Found 5 repositories. Which would you like to clone?
- Specify by number: "Clone 1, 3, 5"
- Specify by name: "Clone user-service and web-dashboard"
- Clone all: "Clone all repositories"
- Filter first: "Show me only Python repos"
```

## Filtering Options

| Filter         | Example                                      |
|----------------|----------------------------------------------|
| By project     | "List repos in the 'backend' project"        |
| By language    | "Show only Python repositories"              |
| By name        | "Find repos containing 'service'"            |
| By activity    | "List repos updated in the last 30 days"     |
| Combined       | "Python repos in backend updated this month" |

## Clone Options

### Single Repository
```
"Clone the user-service repository"
```

### Multiple Repositories (by selection)
```
"Clone repositories 1, 3, and 5 from the list"
```

### All Repositories
```
"Clone all repositories"
"Download everything"
```

### With Custom Directory
```
"Clone user-service to ~/projects/backend/"
```

## Clone Output

For each repository cloned, you'll see:

```
Cloning user-service...
  ✓ Cloned to /home/user/repos/user-service
  - Branch: main
  - Size: 45.2 MB
  - Last commit: "Fix authentication bug" (2 days ago)

Cloning web-dashboard...
  ✓ Cloned to /home/user/repos/web-dashboard
  - Branch: main
  - Size: 128.7 MB
  - Last commit: "Update dependencies" (5 days ago)

Summary: 2 repositories cloned successfully
```

## API Integration

This skill uses the Bitbucket Cloud REST API v2.0. See `references/api-guide.md` for:
- Authentication methods
- Rate limiting considerations
- API endpoint reference
- Error handling

## Reference Files

- **references/config.md** — Authentication and path configuration
- **references/api-guide.md** — Bitbucket API usage and endpoints
- **assets/templates/repo-list.md** — Repository listing format template
- **assets/templates/clone-summary.md** — Clone operation summary template
- **scripts/bitbucket_api.py** — Python helper for API operations

## Security Notes

- **Never commit credentials** — Keep `config.md` in `.gitignore` if sharing
- **Use App Passwords** — More secure than account passwords, can be revoked
- **Minimal permissions** — Only request read access for repository listing
- **Token rotation** — Regularly rotate your access tokens

## Troubleshooting

| Issue                          | Solution                                          |
|--------------------------------|---------------------------------------------------|
| Authentication failed          | Check app password permissions in Bitbucket       |
| Workspace not found            | Verify workspace slug in config.md                |
| Rate limited                   | Wait and retry, or use authenticated requests     |
| Clone permission denied        | Ensure you have repository read access            |
| Repository not found           | Check spelling or use listing to verify name      |
