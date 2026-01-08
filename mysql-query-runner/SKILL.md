---
name: mysql-query-runner
description: Execute MySQL queries against DEV/QA/UAT/PROD databases. Supports environment switching, safe write confirmation, and formatted output. Use when user asks to run SQL queries, check database data, or interact with MySQL databases. Requires VPN connectivity.
version: 1.1.0
---

# MySQL Query Runner

Execute MySQL queries with environment switching and safety guardrails.

## Key Behavior

**Environment Confirmation Required**: If environment is ambiguous or not specified, ASK the user:
- "Which environment should I run this query against? DEV / QA / UAT / PROD"

**Write Operations Require Confirmation**:
- SELECT, SHOW, DESCRIBE, EXPLAIN → Execute freely
- INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE → Require confirmation
- **PROD writes** → Require typing "PROD" to confirm

## Prerequisites

### Stacked Skills
- **vpn-check** — Run `/vpn-check` before any query (required for DB access)
- **credential-setup** — Run `/credential-setup mysql-query-runner` if `.credentials` missing

### Dependencies
```bash
pip install mysql-connector-python
```

---

## Workflow

### Step 1: Verify VPN
```bash
python ~/.claude/skills/vpn-check/scripts/check_vpn.py --quiet
```

### Step 2: Load Credentials
```bash
cat ~/.claude/skills/mysql-query-runner/references/.credentials
```
If missing, invoke `/credential-setup mysql-query-runner`.

### Step 3: Determine Environment
From user request, detect target:
- **Explicit**: "run this on DEV", "query PROD", "in QA"
- **Ambiguous**: No env mentioned → **ASK user**

### Step 4: Execute Query
```bash
python ~/.claude/skills/mysql-query-runner/scripts/mysql_query.py \
    --env <ENV> \
    --query "<SQL>"
```

### Step 5: Return Results
- **SELECT**: Format as markdown table with row count
- **Writes**: Report "X rows affected"
- **Errors**: Show error with suggestions

---

## Script Usage

```bash
# Basic query
python mysql_query.py --env DEV --query "SELECT * FROM users LIMIT 10"

# Show tables
python mysql_query.py --env QA -q "SHOW TABLES"

# Skip LIMIT warning for reads
python mysql_query.py --env UAT -q "SELECT COUNT(*) FROM orders" --yes

# Export to CSV
python mysql_query.py --env DEV -q "SELECT * FROM logs" --format csv --output logs.csv

# Dry run (preview without executing)
python mysql_query.py --env PROD -q "DELETE FROM temp" --dry-run

# Show config (verify connection details)
python mysql_query.py --env DEV --show-config
```

### Arguments

| Argument | Description |
|----------|-------------|
| `--env`, `-e` | Target: DEV, QA, UAT, PROD (prompts if omitted) |
| `--query`, `-q` | SQL query (interactive if omitted) |
| `--format`, `-f` | Output: markdown (default), csv, json |
| `--output`, `-o` | Write results to file |
| `--yes`, `-y` | Skip SELECT LIMIT warning |
| `--dry-run` | Preview without executing |
| `--show-config` | Display connection settings |

---

## Examples

### Read Query
```
User: How many orders are in QA today?

Claude:
1. VPN check: connected
2. Environment: QA (explicit)
3. Query: SELECT COUNT(*) FROM orders WHERE DATE(created_at) = CURDATE()
4. Execute and return markdown table
```

### Write with Confirmation
```
User: Update user 123 email in DEV

Claude:
1. Detects: DEV (explicit), WRITE operation
2. Shows confirmation:

   WRITE OPERATION on DEV

   Query:
   UPDATE users SET email = 'new@example.com' WHERE id = 123

   Proceed? [y/N]
```

### PROD Write (Extra Caution)
```
User: Delete expired sessions from PROD

Claude:
   PRODUCTION WRITE DETECTED

   This will modify the PRODUCTION database.

   Query:
   DELETE FROM sessions WHERE expires_at < NOW()

   Type "PROD" to confirm, or anything else to cancel:
```

---

## Edge Cases

| Case | Handling |
|------|----------|
| No environment specified | Ask: "DEV / QA / UAT / PROD?" |
| Missing credentials | Prompt to run `/credential-setup` |
| Connection refused | Check VPN, verify host/port |
| SELECT without LIMIT | Warn, suggest adding LIMIT |
| Large result set | Output truncates at 50 chars per cell |
| Invalid SQL | Show MySQL error message |

---

## Multi-Database Access

DATABASE is optional in credentials. When not set:
- Use fully qualified table names: `SELECT * FROM intfstagedb.users`
- Switch databases with: `USE metadataconfdb`
- Query across databases: `SELECT * FROM db1.a JOIN db2.b ON ...`
- Run `SHOW DATABASES` to list available databases

Leave `MYSQL_{ENV}_DATABASE=""` in `.credentials` for multi-database access.

---

## Configuration

### Credential Structure
```
MYSQL_{ENV}_HOST     - Database hostname (required)
MYSQL_{ENV}_PORT     - Port (default: 3306)
MYSQL_{ENV}_USER     - Username (required)
MYSQL_{ENV}_PASSWORD - Password (required)
MYSQL_{ENV}_DATABASE - Database name (optional - leave empty for multi-db)
```

### First-Time Setup
```bash
cd ~/.claude/skills/mysql-query-runner/references
cp .credentials.example .credentials
# Edit .credentials with your values
chmod 600 .credentials  # Secure permissions
```
