# Claude Code Skills

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A collection of Claude Code skills to streamline your development workflow: document your coding journey, share insights authentically, and manage Bitbucket repositories directly from Claude Code.

## Skills at a Glance

| Skill | Description | Invoke with |
|-------|-------------|-------------|
| [code-journey-documenter](#code-journey-documenter) | Transform sessions into book chapters | `/code-journey-documenter` |
| [social-media-poster](#social-media-poster) | Convert insights into social posts | `/social-media-poster` |
| [bitbucket-repo-lookup](#bitbucket-repo-lookup) | List and clone Bitbucket repositories | `/bitbucket-repo-lookup` |
| [vpn-check](#vpn-check) | Verify VPN connectivity before internal access | `/vpn-check` |
| [credential-setup](#credential-setup) | Interactive credential configuration helper | `/credential-setup` |
| [deployment-plan-checker](#deployment-plan-checker) | Verify team Bamboo entries in deployment plans | `/deployment-plan-checker` |
| [mysql-query-runner](#mysql-query-runner) | Execute MySQL queries against DEV/QA/UAT/PROD | `/mysql-query-runner` |
| [vault-access](#vault-access) | Retrieve secrets from HashiCorp Vault | `/vault-access` |
| [oracle-query-runner](#oracle-query-runner) | Execute Oracle queries against DEV/QA/UAT/PROD | `/oracle-query-runner` |
| [datadog-api](#datadog-api) | Query Datadog metrics, monitors, and events | `/datadog-api` |
| [s3-access](#s3-access) | Access Amazon S3 buckets and objects | `/s3-access` |
| [sftp-access](#sftp-access) | Access remote SFTP servers for file operations | `/sftp-access` |
| [redis-access](#redis-access) | Access Redis databases with multi-env support | `/redis-access` |
| [aws-sso-env-switcher](#aws-sso-env-switcher) | Switch AWS environments with SSO and kubectl | `/aws-sso-env-switcher` |

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/My-Partner-Source/claude-code-skills.git
   cd claude-code-skills
   ```

2. Install individual skills to `~/.claude/skills/`:
   ```bash
   # Install a specific skill
   cp -r code-journey-documenter ~/.claude/skills/
   cp -r social-media-poster ~/.claude/skills/
   cp -r bitbucket-repo-lookup ~/.claude/skills/
   cp -r vpn-check ~/.claude/skills/
   cp -r credential-setup ~/.claude/skills/
   cp -r deployment-plan-checker ~/.claude/skills/
   cp -r mysql-query-runner ~/.claude/skills/
   cp -r vault-access ~/.claude/skills/
   cp -r oracle-query-runner ~/.claude/skills/
   cp -r datadog-api ~/.claude/skills/
   cp -r s3-access ~/.claude/skills/
   cp -r sftp-access ~/.claude/skills/
   cp -r redis-access ~/.claude/skills/
   cp -r aws-sso-env-switcher ~/.claude/skills/

   # Or install all skills at once
   for skill in */; do
     [ -f "$skill/SKILL.md" ] && cp -r "$skill" ~/.claude/skills/
   done
   ```

3. Skills are now available in Claude Code via their slash commands (e.g., `/vpn-check`).

---

## Code Journey Documenter

Transform coding sessions into book-ready content for "Code With Claude: How AI Transformed the Way I Work (And Think)."

### Core Philosophy

Document mastery through three lenses:
1. **Doing** — Actual coding work with Claude Code
2. **Reflecting** — What worked, failed, surprised
3. **Teaching** — Distillable patterns for readers

### Session Tags

Tag moments during your coding sessions for later processing:

| Tag | Purpose |
|-----|---------|
| `[INSIGHT]` | Key learning moments—things that clicked |
| `[FAILURE]` | What didn't work and why |
| `[PATTERN]` | Recurring strategies worth teaching |
| `[META]` | Reflections on the process itself |

### Workflow

```
1. Pre-Session    → Define job, chapter target, learning objectives
        ↓
2. During-Session → Capture prompts, responses, iterations with tags
        ↓
3. Post-Session   → Run format_session.py to generate chapter draft
        ↓
4. Integration    → Map to book structure and expand
```

### Chapter Draft Structure

Every chapter follows this arc:
1. **Opening Hook** — Real-world problem in vivid terms
2. **The Attempt** — Your approach with Claude Code
3. **The Struggle** — Iterations, failures, pivots
4. **The Breakthrough** — What worked and why
5. **The Pattern** — Generalizable principle
6. **Reader Exercise** — Try-it-yourself prompt

### Script Usage

```bash
# Convert a session log into a chapter draft
python code-journey-documenter/scripts/format_session.py session-2026-01-02.md > chapter-draft.md
```

The script extracts metadata, prompts, iterations, and tagged moments to generate a structured chapter draft.

### Book Structure

The book follows three parts:
- **Part I: Foundations** — Setup, first encounters, mental models
- **Part II: Real-World Mastery** — Job stories, one chapter per project
- **Part III: Beyond** — Meta-reflections, advanced patterns

See `code-journey-documenter/references/book-structure.md` for the complete outline.

---

## Social Media Poster

Generate developer-focused social media content from coding sessions, book chapters, or standalone insights.

### Core Philosophy

> Posts should feel like a smart colleague sharing genuine learnings—not marketing.

The goal is to document the journey publicly, building an audience through authenticity and useful insights.

### Supported Platforms

| Platform | Format | Character Limit | Hashtags |
|----------|--------|-----------------|----------|
| X/Twitter | Single post | 280 | No (discouraged) |
| X/Twitter | Thread | 280 per tweet | No |
| LinkedIn | Post | 3,000 | Yes (2-5 max) |

### Voice Principles

The voice guide emphasizes authenticity over marketing:

1. **Practitioner, Not Pundit** — Write as someone who builds things
2. **Specific Over General** — Concrete details beat abstract principles
3. **Humble Confidence** — Share without excessive hedging or overclaiming
4. **Show the Work** — The journey is more interesting than the destination
5. **Conversational Technical** — Technical accuracy with accessible language

#### Examples

| Avoid | Aim For |
|-------|---------|
| "Developers should really pay more attention to error handling." | "Spent 3 hours on this bug. Here's what I learned." |
| "Optimizing your build pipeline can really improve DX." | "Reduced build time from 4 min to 23 sec by switching to esbuild." |

### Validation Script

```bash
# Validate a post before publishing
python social-media-poster/scripts/validate_post.py post.md
```

The validator checks:
- Platform-specific character limits
- Hashtag compliance (LinkedIn yes, X no)
- Cliché and engagement bait detection
- Voice consistency with the style guide

### Post Frontmatter

```yaml
---
platform: x | x-thread | linkedin
status: draft | ready | posted
created: 2026-01-02
posted: 2026-01-03
session_source: path/to/source-session.md
tags: [claude-code, debugging]
---
```

---

## Bitbucket Repo Lookup

Look up, list, and clone repositories from Bitbucket workspaces without leaving Claude Code.

### Core Philosophy

Bridge the gap between your Bitbucket cloud workspace and local development environment. Instead of manually browsing Bitbucket's web interface, use this skill to discover, search, and clone repositories with natural language commands.

### Workflow

```
1. Authenticate → Set credentials in config.md
        ↓
2. List/Search → Query workspace repos with filters
        ↓
3. Select      → Pick from list or specify "all"
        ↓
4. Clone       → Download to local directory
```

### Quick Start

1. **Set Up Credentials**
   ```bash
   # Copy the credentials template
   cp bitbucket-repo-lookup/references/.credentials.example bitbucket-repo-lookup/references/.credentials

   # Edit .credentials with your Bitbucket credentials
   # Source before using
   source bitbucket-repo-lookup/references/.credentials
   ```

2. **Configure Workspace**
   - Edit `bitbucket-repo-lookup/references/config.md` to set workspace slug and clone directory

3. **List Repositories**
   ```
   "List all repositories in my Bitbucket workspace"
   "Show me repos in the 'backend' project"
   "Find repositories containing 'api' in the name"
   ```

4. **Clone Repositories**
   ```
   "Clone repos 1, 3, and 5"
   "Download all of them"
   "Clone the 'user-service' repository"
   ```

### Filtering Options

| Filter | Example |
|--------|---------|
| By project | "List repos in the 'backend' project" |
| By language | "Show only Python repositories" |
| By name | "Find repos containing 'service'" |
| By activity | "List repos updated in the last 30 days" |
| Combined | "Python repos in backend updated this month" |

### Security Notes

- **Credentials stored separately** — Use `.credentials` file (not checked in) or environment variables
- **Never commit credentials** — `.credentials` is in `.gitignore` to prevent accidental commits
- **Template provided** — Copy `.credentials.example` to `.credentials` and fill in your values
- **Use App Passwords** — More secure than account passwords, can be revoked independently
- **Minimal permissions** — Only request repository read access (sufficient for listing and cloning)
- **Token rotation** — Regularly rotate your access tokens for security

See `bitbucket-repo-lookup/SKILL.md` for complete documentation.

---

## VPN Check

Verify VPN connectivity by checking if internal hostnames can be resolved via DNS. Use standalone or as a prerequisite for skills requiring internal network access.

### Core Philosophy

Fast, reliable VPN detection without requiring authentication or service availability. DNS resolution is the simplest indicator of network connectivity.

### Quick Start

```bash
# First run prompts for configuration
python vpn-check/scripts/check_vpn.py

# After setup, check status
python vpn-check/scripts/check_vpn.py

# Quiet mode for scripting
python vpn-check/scripts/check_vpn.py --quiet
```

### Configuration

On first run, the skill prompts for:
- **Internal hostname** — A hostname only resolvable when on VPN
- **Expected IP** (optional) — For extra validation

Configuration is stored at `~/.claude/skills/vpn-check/.vpn-config` (never committed to git).

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | VPN connected |
| 1 | VPN not connected |
| 2 | Configuration error |

### Skill Stacking

Other skills can use vpn-check as a prerequisite. For example, `bitbucket-repo-lookup` automatically checks VPN status before accessing Bitbucket Server instances.

See `vpn-check/SKILL.md` for complete documentation.

---

## Credential Setup

Interactive helper for setting up credentials from `.credentials.example` templates.

### Core Philosophy

Security through separation: Credentials should never be committed to version control. This skill helps users create `.credentials` files from templates through interactive prompts.

### Quick Start

```bash
# Set up credentials for a skill
python credential-setup/scripts/setup_credentials.py --skill bitbucket-repo-lookup

# Preview without creating
python credential-setup/scripts/setup_credentials.py --skill bitbucket-repo-lookup --dry-run
```

### What It Does

1. Locates `.credentials.example` for the specified skill
2. Parses bash `export` statements to identify required variables
3. Prompts interactively for each credential (with password masking)
4. Creates `.credentials` file with proper permissions (600)
5. Validates against `.gitignore` patterns

### Integration

Skills requiring credentials declare `credential-setup` as a dependency and include a `.credentials.example` template.

See `credential-setup/SKILL.md` for complete documentation.

---

## Deployment Plan Checker

Check deployment plans on Atlassian Confluence to verify team members have completed their Bamboo entries.

### Core Philosophy

Automate the tedious process of checking deployment readiness. Instead of manually scanning Confluence pages for your team's entries, let Claude parse the tables and generate a status report.

### Quick Start

1. **Verify VPN Connection** (required):
   ```
   /vpn-check
   ```
   Must be on VPN to access yourcompany.atlassian.net

2. **Configure Atlassian MCP** (required):
   - Run `/mcp` in Claude Code
   - Authenticate with your Atlassian account
   - Ensure you select the correct Atlassian site during OAuth

3. **Set Up Team Config**:
   ```bash
   cd ~/.claude/skills/deployment-plan-checker/references
   cp .team-config.example .team-config
   # Edit with team member names (one per line)
   ```

4. **Set Up Credentials**:
   ```bash
   cp .credentials.example .credentials
   # Edit with your Atlassian cloudId (UUID format)
   # Find cloudId via: mcp__atlassian__getAccessibleAtlassianResources()
   ```

5. **Check a Deployment Plan**:
   ```
   "Check the deployment plan at https://yourcompany.atlassian.net/wiki/spaces/FD/pages/..."
   "Is my team ready for the QA20260107 deployment?"
   ```

### What It Checks

For each team member in your config, the skill:

1. **Finds their entries** in the "Bamboos" section
2. **Validates completeness** of required fields:
   - Engineering Lead, DevOps, Component/Service
   - Build Link (with env/build info)
   - Config Changes (Y/N/New)
   - Health Checks, Dependencies, Jira Items, Rollback Link
3. **Generates a report** with complete/incomplete/missing entries

### Report Output

```markdown
## Deployment Plan Check: QA20260107 (Jan 7, 2026)

### Bamboo Entry Status
#### ✅ Complete Entries
| Lead | Component | Jira |
|------|-----------|------|
| Alice Smith | my-service | PROJ-1234 |

#### ❌ Incomplete Entries (Action Required)
| Lead | Component | Jira | Missing Fields |
|------|-----------|------|----------------|
| Bob Jones | another-service | PROJ-5678 | Build Link, Rollback Link |

### Summary
- **Status: ✅ READY** or **❌ NOT READY**
```

See `deployment-plan-checker/SKILL.md` for complete documentation.

---

## MySQL Query Runner

Execute MySQL queries against DEV/QA/UAT/PROD environments with safety guardrails and environment switching.

### Core Philosophy

Database operations should be safe by default. Writes require confirmation, PROD writes require extra caution, and environment must be explicit to prevent accidental cross-environment queries.

### Quick Start

1. **Verify VPN Connection** (required):
   ```
   /vpn-check
   ```

2. **Install MySQL Connector**:
   ```bash
   pip install mysql-connector-python
   ```

3. **Set Up Credentials**:
   ```bash
   cd ~/.claude/skills/mysql-query-runner/references
   cp .credentials.example .credentials
   # Edit with your database connection details
   chmod 600 .credentials
   ```

4. **Run Queries**:
   ```
   "Show me the users table in DEV"
   "How many orders are in QA today?"
   "Run SELECT VERSION() on UAT"
   ```

### Safety Features

| Feature | Behavior |
|---------|----------|
| **Environment Required** | Must specify DEV/QA/UAT/PROD (prompts if ambiguous) |
| **Write Confirmation** | INSERT/UPDATE/DELETE require explicit confirmation |
| **PROD Protection** | PROD writes require typing "PROD" to confirm |
| **LIMIT Warning** | Warns if SELECT has no LIMIT clause |

### Multi-Database Access

DATABASE is optional in credentials. Leave empty to access multiple databases:

```sql
-- Use fully qualified table names
SELECT * FROM intfstagedb.users;
SELECT * FROM metadataconfdb.config WHERE id = 1;

-- Or switch databases
USE intfstagedb;
SELECT * FROM users;
```

### Script Usage

```bash
# Basic query
python mysql_query.py --env DEV --query "SELECT * FROM users LIMIT 10"

# Export to CSV
python mysql_query.py --env QA -q "SELECT * FROM logs" --format csv --output logs.csv

# Dry run (preview without executing)
python mysql_query.py --env PROD -q "DELETE FROM temp" --dry-run

# Show config
python mysql_query.py --env DEV --show-config
```

### Output Formats

| Format | Use Case |
|--------|----------|
| `markdown` (default) | Clean tables for chat display |
| `csv` | Export for spreadsheets |
| `json` | Programmatic processing |

See `mysql-query-runner/SKILL.md` for complete documentation.

---

## Vault Access

Retrieve secrets from HashiCorp Vault with KV v1/v2 engine support and secure credential handling.

### Core Philosophy

Secrets should be managed securely and accessed programmatically. This skill connects to HashiCorp Vault to retrieve credentials, API keys, and other sensitive data without exposing them in logs or history.

### Quick Start

1. **Verify VPN Connection** (if internal Vault):
   ```
   /vpn-check
   ```

2. **Run Setup Script** (creates venv and installs dependencies):
   ```bash
   cd ~/.claude/skills/vault-access && bash setup.sh
   ```

3. **Set Up Credentials**:
   ```bash
   cd ~/.claude/skills/vault-access/references
   cp .credentials.example .credentials
   # Edit with your Vault address and token
   chmod 600 .credentials
   ```

4. **Retrieve Secrets**:
   ```
   "Get the database password from Vault"
   "List secrets under secret/myapp/"
   "Check Vault connection status"
   ```

### Commands

| Command | Description |
|---------|-------------|
| `get <path>` | Retrieve secret(s) from a path |
| `list <path>` | List secrets at a path |
| `status` | Check Vault connectivity and auth status |

### Script Usage

```bash
# Get all keys from a secret
~/.claude/skills/vault-access/scripts/vault_access.py get secret/myapp/database

# Get a specific key
~/.claude/skills/vault-access/scripts/vault_access.py get secret/myapp/database --key password

# List secrets
~/.claude/skills/vault-access/scripts/vault_access.py list secret/myapp/

# Show actual values (default: masked)
~/.claude/skills/vault-access/scripts/vault_access.py get secret/myapp/database --show

# Export as environment variables
~/.claude/skills/vault-access/scripts/vault_access.py get secret/myapp/database --format env
```

### Output Formats

| Format | Use Case |
|--------|----------|
| `table` (default) | Clean key-value display (masked) |
| `json` | Programmatic processing |
| `env` | Shell export statements |
| `raw` | Single value (requires --key) |

### Security Features

- **Masked by default** — Secret values shown as `ab****cd`
- **Token authentication** — Uses Vault tokens (short-lived preferred)
- **No logging** — Secrets never written to logs
- **File permissions** — `.credentials` set to 600 (owner only)

See `vault-access/SKILL.md` for complete documentation.

---

## Oracle Query Runner

Execute Oracle SQL queries against DEV/QA/UAT/PROD environments with safety guardrails and environment switching.

### Core Philosophy

Database operations should be safe by default. Writes require confirmation, PROD writes require extra caution, and environment must be explicit to prevent accidental cross-environment queries.

### Quick Start

1. **Verify VPN Connection** (required):
   ```
   /vpn-check
   ```

2. **Run Setup** (creates virtual environment and installs oracledb):
   ```bash
   cd ~/.claude/skills/oracle-query-runner && bash setup.sh
   ```

3. **Set Up Credentials**:
   ```bash
   cd ~/.claude/skills/oracle-query-runner/references
   cp .credentials.example .credentials
   # Edit with your database connection details
   chmod 600 .credentials
   ```

4. **Run Queries**:
   ```
   "Show me the users table in DEV"
   "How many orders are in QA today?"
   "Run SELECT * FROM v$version on UAT"
   ```

### Safety Features

| Feature | Behavior |
|---------|----------|
| **Environment Required** | Must specify DEV/QA/UAT/PROD (prompts if ambiguous) |
| **Write Confirmation** | INSERT/UPDATE/DELETE require explicit confirmation |
| **PROD Protection** | PROD writes require typing "PROD" to confirm |
| **ROWNUM Warning** | Warns if SELECT has no ROWNUM/FETCH clause |

### Oracle Connection

Uses Easy Connect format: `host:port/service_name`

The driver uses "thin" mode by default (no Oracle Instant Client required). For advanced features requiring "thick" mode, install Oracle Instant Client separately.

### Script Usage

```bash
# Basic query
oracle_query.py --env DEV --query "SELECT * FROM users WHERE ROWNUM <= 10"

# Export to CSV
oracle_query.py --env QA -q "SELECT * FROM logs WHERE ROWNUM <= 100" --format csv --output logs.csv

# Dry run (preview without executing)
oracle_query.py --env PROD -q "DELETE FROM temp" --dry-run

# Show config
oracle_query.py --env DEV --show-config
```

### Output Formats

| Format | Use Case |
|--------|----------|
| `markdown` (default) | Clean tables for chat display |
| `csv` | Export for spreadsheets |
| `json` | Programmatic processing |

See `oracle-query-runner/SKILL.md` for complete documentation.

---

## Datadog API

Query Datadog metrics, monitors, dashboards, and events for observability insights directly from Claude Code.

### Core Philosophy

Access your Datadog observability data without context switching. Query metrics, check alert status, and investigate incidents from your development environment.

### Quick Start

1. **Install Dependencies** (creates virtual environment):
   ```bash
   cd ~/.claude/skills/datadog-api && bash setup.sh
   ```

2. **Set Up Credentials**:
   ```bash
   cd ~/.claude/skills/datadog-api/references
   cp .credentials.example .credentials
   # Edit with your Datadog API and Application keys
   chmod 600 .credentials
   ```

3. **Query Data**:
   ```
   "Are there any alerts firing right now?"
   "What's the CPU usage on prod-web-01 over the last hour?"
   "Show me dashboards related to production"
   ```

### Commands

| Command | Description |
|---------|-------------|
| `monitors` | List monitors with optional status/tag filtering |
| `query` | Query time-series metrics |
| `dashboards` | List dashboards with optional name filter |
| `events` | List events with time range and tag filtering |
| `monitor-info` | Get detailed monitor information |
| `dashboard-info` | Get dashboard definition |

### Script Usage

```bash
# List alerting monitors
python datadog-api/scripts/datadog_api.py monitors --status alerting

# Query CPU metrics
python datadog-api/scripts/datadog_api.py query --metric system.cpu.user --from 2 --tags host:prod-web-01

# List dashboards
python datadog-api/scripts/datadog_api.py dashboards --filter production

# Get recent events
python datadog-api/scripts/datadog_api.py events --from 24 --tags service:api
```

### Datadog Sites

| Site | Region |
|------|--------|
| `datadoghq.com` | US1 (default) |
| `us3.datadoghq.com` | US3 |
| `us5.datadoghq.com` | US5 |
| `datadoghq.eu` | EU1 |
| `ap1.datadoghq.com` | AP1 |
| `ddog-gov.com` | US Government |

See `datadog-api/SKILL.md` for complete documentation.

---

## S3 Access

Access Amazon S3 buckets and objects with multi-profile and region support directly from Claude Code.

### Core Philosophy

Interact with your S3 storage without leaving your development environment. List buckets, browse objects, and transfer files with simple commands.

### Quick Start

1. **Install Dependencies** (creates virtual environment):
   ```bash
   cd ~/.claude/skills/s3-access && bash setup.sh
   ```

2. **Set Up Credentials**:
   ```bash
   cd ~/.claude/skills/s3-access/references
   cp .credentials.example .credentials
   # Edit with your AWS credentials
   chmod 600 .credentials
   ```

3. **Access S3**:
   ```
   "List my S3 buckets"
   "Show files in the logs bucket"
   "Download config.json from my-bucket"
   ```

### Commands

| Command | Description |
|---------|-------------|
| `buckets` | List all accessible S3 buckets |
| `ls <bucket>[/prefix]` | List objects with optional prefix filter |
| `get <bucket/key>` | Get object contents or download to file |
| `put <local> <bucket/key>` | Upload local file to S3 |
| `info <bucket/key>` | Get object metadata (size, type, modified) |
| `rm <bucket/key>` | Delete an object (with confirmation) |
| `cp <src> <dest>` | Copy object between locations |

### Script Usage

```bash
# List buckets
~/.claude/skills/s3-access/scripts/s3_access.py buckets

# List objects
~/.claude/skills/s3-access/scripts/s3_access.py ls my-bucket/logs/

# Download file
~/.claude/skills/s3-access/scripts/s3_access.py get my-bucket/config.json --output local.json

# Upload file
~/.claude/skills/s3-access/scripts/s3_access.py put report.pdf my-bucket/reports/report.pdf

# Use specific profile/region
~/.claude/skills/s3-access/scripts/s3_access.py buckets --profile production --region eu-west-1
```

### Multi-Profile Support

Use AWS profiles from `~/.aws/credentials`:

```bash
~/.claude/skills/s3-access/scripts/s3_access.py buckets --profile production
~/.claude/skills/s3-access/scripts/s3_access.py ls my-bucket --profile staging
```

### Custom Endpoints

Connect to S3-compatible services (MinIO, LocalStack, VPC endpoints):

```bash
~/.claude/skills/s3-access/scripts/s3_access.py buckets --endpoint-url http://localhost:9000
```

See `s3-access/SKILL.md` for complete documentation.

---

## SFTP Access

Access remote SFTP servers for file transfer and management operations with password or SSH key authentication.

### Core Philosophy

Transfer files to and from SFTP servers without leaving your development environment. Supports both password and SSH key authentication for secure connections.

### Quick Start

1. **Install Dependencies** (creates virtual environment):
   ```bash
   cd ~/.claude/skills/sftp-access && bash setup.sh
   ```

2. **Set Up Credentials**:
   ```bash
   cd ~/.claude/skills/sftp-access/references
   cp .credentials.example .credentials
   # Edit with your SFTP host and credentials
   chmod 600 .credentials
   ```

3. **Access SFTP**:
   ```
   "List files on the SFTP server"
   "Download the config file from /etc/app/"
   "Upload report.pdf to /uploads/"
   ```

### Commands

| Command | Description |
|---------|-------------|
| `ls <path>` | List remote directory contents |
| `get <path>` | Get file contents or download to file |
| `put <local> <remote>` | Upload local file to SFTP server |
| `info <path>` | Get file/directory metadata |
| `rm <path>` | Delete a remote file |
| `mkdir <path>` | Create remote directory |
| `rmdir <path>` | Remove remote directory (must be empty) |

### Script Usage

```bash
# List directory
~/.claude/skills/sftp-access/scripts/sftp_access.py ls /var/log

# Download file
~/.claude/skills/sftp-access/scripts/sftp_access.py get /etc/app/config.yaml --output config.yaml

# Upload file
~/.claude/skills/sftp-access/scripts/sftp_access.py put report.pdf /uploads/report.pdf

# Get file info
~/.claude/skills/sftp-access/scripts/sftp_access.py info /var/log/app.log

# Use specific host/user
~/.claude/skills/sftp-access/scripts/sftp_access.py ls /home --host sftp.example.com --user myuser
```

### Authentication Methods

**Password Authentication:**
```bash
# Set in .credentials file
SFTP_PASSWORD="your-password"
```

**SSH Key Authentication:**
```bash
# Set key path in .credentials
SFTP_KEY_FILE="/home/user/.ssh/id_ed25519"

# Or use CLI argument
~/.claude/skills/sftp-access/scripts/sftp_access.py ls /path --key ~/.ssh/id_rsa
```

**Encrypted Keys:**
```bash
# Set passphrase for encrypted keys
SFTP_KEY_PASSPHRASE="your-key-passphrase"
```

Supports Ed25519, RSA, ECDSA, and DSS key types.

### Security Notes

- Use SSH keys instead of passwords when possible
- Set `.credentials` file permissions to 600
- Rotate credentials regularly
- Never commit credentials to version control

See `sftp-access/SKILL.md` for complete documentation.

---

## Redis Access

Access Redis databases across DEV/QA/UAT/PROD environments with comprehensive data type support and safety guardrails.

### Core Philosophy

Database operations should be safe by default. Writes require confirmation, PROD writes require extra caution, and environment must be explicit to prevent accidental operations.

### Quick Start

1. **Verify VPN Connection** (if internal Redis):
   ```
   /vpn-check
   ```

2. **Install Dependencies** (creates virtual environment):
   ```bash
   cd ~/.claude/skills/redis-access && bash setup.sh
   ```

3. **Set Up Credentials**:
   ```bash
   cd ~/.claude/skills/redis-access/references
   cp .credentials.example .credentials
   # Edit with your Redis connection details for each environment
   chmod 600 .credentials
   ```

4. **Access Redis**:
   ```
   "Get the session key from DEV Redis"
   "List all cache keys matching 'user:*' in QA"
   "Check Redis memory usage in PROD"
   ```

### Supported Data Types

| Type | Commands |
|------|----------|
| **Strings** | `get`, `set`, `del` |
| **Hashes** | `hget`, `hset`, `hgetall`, `hdel`, `hkeys`, `hlen` |
| **Lists** | `lrange`, `lpush`, `rpush`, `llen`, `lpop`, `rpop` |
| **Sets** | `smembers`, `sadd`, `srem`, `sismember`, `scard` |
| **Sorted Sets** | `zrange`, `zadd`, `zscore`, `zrem`, `zcard` |
| **Keys** | `keys`, `type`, `ttl`, `exists`, `expire` |
| **Server** | `info`, `dbsize`, `ping` |

### Script Usage

```bash
# String operations
~/.claude/skills/redis-access/scripts/redis_access.py --env DEV get mykey
~/.claude/skills/redis-access/scripts/redis_access.py --env DEV set mykey "value" --ttl 3600

# Hash operations
~/.claude/skills/redis-access/scripts/redis_access.py --env QA hgetall session:user:123

# Key operations
~/.claude/skills/redis-access/scripts/redis_access.py --env UAT keys "cache:*"

# Server info
~/.claude/skills/redis-access/scripts/redis_access.py --env PROD info --section memory
```

### Safety Features

| Feature | Behavior |
|---------|----------|
| **Environment Required** | Must specify DEV/QA/UAT/PROD |
| **Write Confirmation** | SET, DEL, HSET, etc. require confirmation |
| **PROD Protection** | PROD writes require typing "PROD" to confirm |
| **Dry Run** | Preview operations with `--dry-run` |

### Output Formats

| Format | Use Case |
|--------|----------|
| `text` (default) | Clean display for chat |
| `json` | Programmatic processing |

See `redis-access/SKILL.md` for complete documentation.

---

## AWS SSO Environment Switcher

Switch between AWS environments (DEV/QA/UAT/PROD) using AWS SSO and manage kubectl contexts for EKS clusters.

### Core Philosophy

Eliminate the friction of managing multiple AWS accounts and Kubernetes clusters. Switch environments with a single command, and your SSO session and kubectl context are automatically configured.

### Quick Start

1. **Verify Prerequisites**:
   ```bash
   # AWS CLI v2 required for SSO
   aws --version  # Should be 2.x

   # kubectl required for EKS
   kubectl version --client
   ```

2. **Install Dependencies** (creates virtual environment):
   ```bash
   cd ~/.claude/skills/aws-sso-env-switcher && bash setup.sh
   ```

3. **Set Up Credentials**:
   ```bash
   cd ~/.claude/skills/aws-sso-env-switcher/references
   cp .credentials.example .credentials
   # Edit with your AWS SSO and EKS details
   chmod 600 .credentials
   ```

4. **Switch Environments**:
   ```
   "Switch to the DEV environment"
   "Connect to QA and show pods"
   "Get deployments from PROD"
   ```

### Commands

| Command | Description |
|---------|-------------|
| `status` | Check SSO authentication status for all environments |
| `switch --env <ENV>` | Switch to environment (DEV/QA/UAT/PROD) |
| `kubectl --env <ENV> -- <args>` | Run kubectl command in environment |
| `list` | List configured environments |
| `current` | Show current environment and context |
| `login --env <ENV>` | Force SSO login for environment |
| `update-kubeconfig --env <ENV>` | Update kubectl config for EKS cluster |

### Script Usage

```bash
# Check SSO status
~/.claude/skills/aws-sso-env-switcher/scripts/aws_sso_env.py status

# Switch environment
~/.claude/skills/aws-sso-env-switcher/scripts/aws_sso_env.py switch --env DEV

# Run kubectl in specific environment
~/.claude/skills/aws-sso-env-switcher/scripts/aws_sso_env.py kubectl --env PROD -- get pods
~/.claude/skills/aws-sso-env-switcher/scripts/aws_sso_env.py kubectl --env QA -- get deployments -n my-namespace
~/.claude/skills/aws-sso-env-switcher/scripts/aws_sso_env.py kubectl -- logs deployment/my-app

# List environments
~/.claude/skills/aws-sso-env-switcher/scripts/aws_sso_env.py list
```

### Safety Features

| Feature | Behavior |
|---------|----------|
| **Environment Display** | Always shows current environment before operations |
| **PROD Protection** | Destructive kubectl operations in PROD require typing "PROD" to confirm |
| **Auto SSO Refresh** | Automatically re-authenticates when session expires |
| **Context Isolation** | Each environment uses distinct kubectl context |

### Credential Structure

```bash
# AWS SSO Configuration
AWS_SSO_START_URL="https://mycompany.awsapps.com/start"
AWS_SSO_REGION="us-east-1"

# Per-Environment Configuration
AWS_DEV_SSO_ACCOUNT_ID="123456789012"
AWS_DEV_SSO_ROLE_NAME="DeveloperAccess"
AWS_DEV_EKS_CLUSTER="my-app-dev-eks"
AWS_DEV_EKS_REGION="us-east-1"
AWS_DEV_NAMESPACE="default"

# Repeat for QA, UAT, PROD...
```

### AWS SSO Setup

The skill automatically creates AWS CLI profiles for each environment:

```bash
# In ~/.aws/config (auto-generated)
[profile dev-sso]
sso_start_url = https://mycompany.awsapps.com/start
sso_region = us-east-1
sso_account_id = 123456789012
sso_role_name = DeveloperAccess
region = us-east-1
```

### Destructive Operations

These kubectl operations require explicit confirmation in PROD:
- `delete` — Deletes resources
- `scale` — Scales deployments (especially to zero)
- `rollout restart` — Restarts deployments
- `apply` — Applies configuration changes
- `patch` — Patches resources

See `aws-sso-env-switcher/SKILL.md` for complete documentation.

---

## Configuration

Each skill has its own configuration file. Edit the `references/config.md` file in each skill directory to customize paths and settings.

### Default Paths

| Skill | Output Directory |
|-------|------------------|
| code-journey-documenter | `~/dev/personal/books/code-with-claude` |
| social-media-poster | `~/dev/personal/social-posts` |
| bitbucket-repo-lookup | `~/repos` (clone destination) |
| vpn-check | `~/.claude/skills/vpn-check/.vpn-config` |
| credential-setup | Creates `.credentials` in skill's `references/` directory |
| deployment-plan-checker | `~/.claude/skills/deployment-plan-checker/references/` |
| mysql-query-runner | `~/.claude/skills/mysql-query-runner/references/.credentials` |
| vault-access | `~/.claude/skills/vault-access/references/.credentials` |
| oracle-query-runner | `~/.claude/skills/oracle-query-runner/references/.credentials` |
| datadog-api | `~/.claude/skills/datadog-api/references/.credentials` |
| s3-access | `~/.claude/skills/s3-access/references/.credentials` |
| sftp-access | `~/.claude/skills/sftp-access/references/.credentials` |
| redis-access | `~/.claude/skills/redis-access/references/.credentials` |
| aws-sso-env-switcher | `~/.claude/skills/aws-sso-env-switcher/references/.credentials` |

### Directory Structure (Book)

```
~/dev/personal/books/code-with-claude/
├── chapters/
│   ├── part-1/
│   ├── part-2/
│   └── part-3/
├── sessions/          # Raw session logs
├── code-examples/     # Referenced code snippets
├── drafts/            # Work in progress
└── assets/            # Images, diagrams
```

### Directory Structure (Social Posts)

```
~/dev/personal/social-posts/
├── x/
│   ├── drafts/
│   ├── ready/
│   ├── posted/
│   └── threads/
└── linkedin/
    ├── drafts/
    ├── ready/
    └── posted/
```

---

## Project Structure

```
claude-code-skills/
├── README.md
├── AGENTS.md                             # AI assistant context
├── LICENSE
├── .gitignore
│
├── code-journey-documenter/
│   ├── SKILL.md                          # Skill definition
│   ├── assets/
│   │   └── chapter-templates/
│   │       ├── foundation-chapter.md     # Part I template
│   │       ├── job-story-chapter.md      # Part II template
│   │       └── meta-chapter.md           # Part III template
│   ├── references/
│   │   ├── config.md                     # Path configuration
│   │   ├── book-structure.md             # Complete book outline
│   │   ├── pattern-library.md            # Collected patterns
│   │   └── session-template.md           # Session logging format
│   └── scripts/
│       └── format_session.py             # Session → Chapter converter
│
├── social-media-poster/
│   ├── SKILL.md                          # Skill definition
│   ├── assets/
│   │   └── templates/
│   │       ├── x-single.md               # Single tweet template
│   │       ├── x-thread.md               # Thread template
│   │       └── linkedin.md               # LinkedIn post template
│   ├── references/
│   │   ├── config.md                     # Path configuration
│   │   ├── platform-x.md                 # X/Twitter best practices
│   │   ├── platform-linkedin.md          # LinkedIn best practices
│   │   └── voice-guide.md                # Writing style guide
│   └── scripts/
│       └── validate_post.py              # Post validator
│
├── bitbucket-repo-lookup/
│   ├── SKILL.md                          # Skill definition
│   ├── assets/
│   │   └── templates/
│   │       ├── repo-list.md              # Repository listing template
│   │       └── clone-summary.md          # Clone summary template
│   ├── references/
│   │   ├── config.md                     # Path and auth configuration
│   │   ├── api-guide.md                  # Bitbucket API reference
│   │   └── .credentials.example          # Credentials template
│   └── scripts/
│       └── bitbucket_api.py              # API helper script
│
├── vpn-check/
│   ├── SKILL.md                          # Skill definition
│   ├── references/
│   │   └── .vpn-config.example           # Configuration template
│   └── scripts/
│       └── check_vpn.py                  # VPN connectivity checker
│
├── credential-setup/
│   ├── SKILL.md                          # Skill definition
│   ├── references/
│   │   └── usage-guide.md                # Integration guide
│   └── scripts/
│       └── setup_credentials.py          # Interactive credential setup
│
├── deployment-plan-checker/
│   ├── SKILL.md                          # Skill definition
│   └── references/
│       ├── .team-config.example          # Team member template
│       ├── .credentials.example          # Atlassian cloudId template
│       └── .gitignore                    # Protects credentials
│
├── mysql-query-runner/
│   ├── SKILL.md                          # Skill definition
│   ├── references/
│   │   ├── .credentials.example          # Database credentials template
│   │   └── .gitignore                    # Protects credentials
│   └── scripts/
│       └── mysql_query.py                # MySQL query executor with safety checks
│
├── vault-access/
│   ├── SKILL.md                          # Skill definition
│   ├── setup.sh                          # Virtual environment setup
│   ├── requirements.txt                  # Python dependencies
│   ├── references/
│   │   ├── .credentials.example          # Vault credentials template
│   │   └── .gitignore                    # Protects credentials
│   └── scripts/
│       └── vault_access.py               # Vault secret retrieval
│
├── oracle-query-runner/
│   ├── SKILL.md                          # Skill definition
│   ├── setup.sh                          # Virtual environment setup
│   ├── requirements.txt                  # Python dependencies (oracledb)
│   ├── references/
│   │   ├── .credentials.example          # Oracle credentials template
│   │   └── .gitignore                    # Protects credentials
│   └── scripts/
│       └── oracle_query.py               # Oracle query executor with safety checks
│
├── datadog-api/
│   ├── SKILL.md                          # Skill definition
│   ├── setup.sh                          # Virtual environment setup
│   ├── requirements.txt                  # Python dependencies (requests)
│   ├── references/
│   │   ├── .credentials.example          # API credentials template
│   │   └── .gitignore                    # Protects credentials
│   └── scripts/
│       └── datadog_api.py                # Datadog API wrapper
│
├── s3-access/
│   ├── SKILL.md                          # Skill definition
│   ├── setup.sh                          # Virtual environment setup
│   ├── requirements.txt                  # Python dependencies (boto3)
│   ├── references/
│   │   ├── .credentials.example          # AWS credentials template
│   │   └── .gitignore                    # Protects credentials
│   └── scripts/
│       └── s3_access.py                  # S3 access wrapper
│
├── sftp-access/
│   ├── SKILL.md                          # Skill definition
│   ├── setup.sh                          # Virtual environment setup
│   ├── requirements.txt                  # Python dependencies (paramiko)
│   ├── references/
│   │   ├── .credentials.example          # SFTP credentials template
│   │   └── .gitignore                    # Protects credentials
│   └── scripts/
│       └── sftp_access.py                # SFTP access wrapper
│
├── redis-access/
│   ├── SKILL.md                          # Skill definition
│   ├── setup.sh                          # Virtual environment setup
│   ├── requirements.txt                  # Python dependencies (redis)
│   ├── references/
│   │   ├── .credentials.example          # Redis credentials template
│   │   └── .gitignore                    # Protects credentials
│   └── scripts/
│       └── redis_access.py               # Redis access wrapper
│
└── aws-sso-env-switcher/
    ├── SKILL.md                          # Skill definition
    ├── setup.sh                          # Virtual environment setup
    ├── requirements.txt                  # Python dependencies (boto3)
    ├── references/
    │   ├── .credentials.example          # AWS SSO and EKS config template
    │   └── .gitignore                    # Protects credentials
    └── scripts/
        └── aws_sso_env.py                # AWS SSO environment switcher
```

---

## Author

**David Rutgos**
- Email: [david.rutgos@gmail.com](mailto:david.rutgos@gmail.com)
- LinkedIn: [linkedin.com/in/davidrutgos](https://www.linkedin.com/in/davidrutgos/)
- X: [@DavidRutgos](https://x.com/DavidRutgos)

---

## Contributing

Contributions are welcome! If you have ideas for improving these skills or want to share your own Claude Code workflows:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/improvement`)
3. Commit your changes (`git commit -am 'Add improvement'`)
4. Push to the branch (`git push origin feature/improvement`)
5. Open a Pull Request

---

## License

MIT License - see [LICENSE](LICENSE) for details.

Copyright (c) 2026 My Partner Source
