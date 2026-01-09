---
name: oracle-query-runner
description: Execute Oracle SQL queries against DEV/QA/UAT/PROD databases. Supports environment switching, safe write confirmation, and formatted output. Use when user asks to run Oracle SQL queries, check database data, or interact with Oracle databases. Requires VPN connectivity.
version: 1.0.0
---

# Oracle Query Runner

Execute Oracle SQL queries with environment switching and safety guardrails.

## Key Behavior

**Environment Confirmation Required**: If environment is ambiguous or not specified, ASK the user:
- "Which environment should I run this query against? DEV / QA / UAT / PROD"

**Write Operations Require Confirmation**:
- SELECT, DESCRIBE, EXPLAIN → Execute freely
- INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE → Require confirmation
- **PROD writes** → Require typing "PROD" to confirm

## Prerequisites

### Stacked Skills
- **vpn-check** — Run `/vpn-check` before any query (required for DB access)
- **credential-setup** — Run `/credential-setup oracle-query-runner` if `.credentials` missing

### Dependencies

**One-time setup** (creates virtual environment and installs oracledb):

```bash
cd ~/.claude/skills/oracle-query-runner && bash setup.sh
```

This creates a `.venv` folder and configures the script to use it automatically.

**Oracle Instant Client**: For thick mode (required for some Oracle features), install Oracle Instant Client:
- macOS: `brew install instantclient-basic`
- Linux: Download from [Oracle](https://www.oracle.com/database/technologies/instant-client/downloads.html)

The script works in thin mode by default (no Instant Client needed for most use cases).

---

## Workflow

### Step 1: Verify VPN
```bash
python ~/.claude/skills/vpn-check/scripts/check_vpn.py --quiet
```

### Step 2: Load Credentials
```bash
cat ~/.claude/skills/oracle-query-runner/references/.credentials
```
If missing, invoke `/credential-setup oracle-query-runner`.

### Step 3: Determine Environment
From user request, detect target:
- **Explicit**: "run this on DEV", "query PROD", "in QA"
- **Ambiguous**: No env mentioned → **ASK user**

### Step 4: Execute Query
```bash
~/.claude/skills/oracle-query-runner/scripts/oracle_query.py \
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
~/.claude/skills/oracle-query-runner/scripts/oracle_query.py --env DEV --query "SELECT * FROM users WHERE ROWNUM <= 10"

# Show tables
~/.claude/skills/oracle-query-runner/scripts/oracle_query.py --env QA -q "SELECT table_name FROM user_tables"

# Skip ROWNUM warning for reads
~/.claude/skills/oracle-query-runner/scripts/oracle_query.py --env UAT -q "SELECT COUNT(*) FROM orders" --yes

# Export to CSV
~/.claude/skills/oracle-query-runner/scripts/oracle_query.py --env DEV -q "SELECT * FROM logs WHERE ROWNUM <= 100" --format csv --output logs.csv

# Dry run (preview without executing)
~/.claude/skills/oracle-query-runner/scripts/oracle_query.py --env PROD -q "DELETE FROM temp_table" --dry-run

# Show config (verify connection details)
~/.claude/skills/oracle-query-runner/scripts/oracle_query.py --env DEV --show-config
```

### Arguments

| Argument | Description |
|----------|-------------|
| `--env`, `-e` | Target: DEV, QA, UAT, PROD (prompts if omitted) |
| `--query`, `-q` | SQL query (interactive if omitted) |
| `--format`, `-f` | Output: markdown (default), csv, json |
| `--output`, `-o` | Write results to file |
| `--yes`, `-y` | Skip SELECT ROWNUM warning |
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
3. Query: SELECT COUNT(*) FROM orders WHERE TRUNC(created_at) = TRUNC(SYSDATE)
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
   DELETE FROM sessions WHERE expires_at < SYSDATE

   Type "PROD" to confirm, or anything else to cancel:
```

---

## Edge Cases

| Case | Handling |
|------|----------|
| No environment specified | Ask: "DEV / QA / UAT / PROD?" |
| Missing credentials | Prompt to run `/credential-setup` |
| Connection refused | Check VPN, verify host/port/service |
| SELECT without ROWNUM/FETCH | Warn, suggest adding row limit |
| Large result set | Output truncates at 50 chars per cell |
| Invalid SQL | Show Oracle error message (ORA-XXXXX) |

---

## Oracle Connection Methods

The skill supports multiple Oracle connection string formats:

### Easy Connect (recommended)
```
host:port/service_name
```

### TNS Connect
```
(DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)(HOST=host)(PORT=port))(CONNECT_DATA=(SERVICE_NAME=service)))
```

### Service Name vs SID
- **SERVICE_NAME**: Modern, recommended (maps to multiple instances)
- **SID**: Legacy, instance-specific

Use SERVICE_NAME unless connecting to legacy databases.

---

## Configuration

### Credential Structure
```
ORACLE_{ENV}_HOST     - Database hostname (required)
ORACLE_{ENV}_PORT     - Port (default: 1521)
ORACLE_{ENV}_USER     - Username (required)
ORACLE_{ENV}_PASSWORD - Password (required)
ORACLE_{ENV}_SERVICE  - Service name (required)
```

### First-Time Setup
```bash
cd ~/.claude/skills/oracle-query-runner/references
cp .credentials.example .credentials
# Edit .credentials with your values
chmod 600 .credentials  # Secure permissions
```
