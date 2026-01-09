---
name: redis-access
description: "Access Redis databases with multi-environment support (DEV/QA/UAT/PROD), supporting strings, lists, hashes, sets, and sorted sets with safety guardrails"
version: 1.0.0
author: David Rutgos
---

# Redis Access Skill

Access Redis databases across DEV/QA/UAT/PROD environments with comprehensive data type support and safety guardrails.

## Purpose

Enable quick Redis data inspection and manipulation from the command line with:
- Multi-environment support (DEV, QA, UAT, PROD)
- All major Redis data types (strings, lists, hashes, sets, sorted sets)
- Safety features for production environments
- Credential auto-loading from `.credentials` file

## Dependencies

| Skill | Path | Purpose |
|-------|------|---------|
| vpn-check | `vpn-check/SKILL.md` | Verify VPN connectivity before accessing internal Redis instances |

## One-Time Setup

```bash
cd ~/.claude/skills/redis-access && bash setup.sh
```

This creates a virtual environment and installs the `redis` Python package.

## Configuration

Copy the example credentials file and fill in your values:

```bash
cp references/.credentials.example references/.credentials
chmod 600 references/.credentials
```

### Credentials Format

```bash
# DEV Environment
export REDIS_DEV_HOST="redis-dev.internal.example.com"
export REDIS_DEV_PORT="6379"
export REDIS_DEV_PASSWORD=""
export REDIS_DEV_DB="0"

# QA Environment
export REDIS_QA_HOST="redis-qa.internal.example.com"
export REDIS_QA_PORT="6379"
export REDIS_QA_PASSWORD=""
export REDIS_QA_DB="0"

# UAT Environment
export REDIS_UAT_HOST="redis-uat.internal.example.com"
export REDIS_UAT_PORT="6379"
export REDIS_UAT_PASSWORD=""
export REDIS_UAT_DB="0"

# PROD Environment
export REDIS_PROD_HOST="redis-prod.internal.example.com"
export REDIS_PROD_PORT="6379"
export REDIS_PROD_PASSWORD=""
export REDIS_PROD_DB="0"
```

## Usage

### String Operations

```bash
# Get a key value
~/.claude/skills/redis-access/scripts/redis_access.py --env DEV get mykey

# Set a key value
~/.claude/skills/redis-access/scripts/redis_access.py --env DEV set mykey "myvalue"

# Set with TTL (seconds)
~/.claude/skills/redis-access/scripts/redis_access.py --env DEV set mykey "myvalue" --ttl 3600

# Delete a key
~/.claude/skills/redis-access/scripts/redis_access.py --env DEV del mykey
```

### Key Operations

```bash
# List keys matching pattern
~/.claude/skills/redis-access/scripts/redis_access.py --env DEV keys "user:*"

# Get key type
~/.claude/skills/redis-access/scripts/redis_access.py --env DEV type mykey

# Get TTL for a key
~/.claude/skills/redis-access/scripts/redis_access.py --env DEV ttl mykey

# Check if key exists
~/.claude/skills/redis-access/scripts/redis_access.py --env DEV exists mykey
```

### Hash Operations

```bash
# Get hash field
~/.claude/skills/redis-access/scripts/redis_access.py --env DEV hget myhash field

# Set hash field
~/.claude/skills/redis-access/scripts/redis_access.py --env DEV hset myhash field "value"

# Get all hash fields
~/.claude/skills/redis-access/scripts/redis_access.py --env DEV hgetall myhash

# Delete hash field
~/.claude/skills/redis-access/scripts/redis_access.py --env DEV hdel myhash field
```

### List Operations

```bash
# Get list range
~/.claude/skills/redis-access/scripts/redis_access.py --env DEV lrange mylist 0 -1

# Push to list (left)
~/.claude/skills/redis-access/scripts/redis_access.py --env DEV lpush mylist "value"

# Push to list (right)
~/.claude/skills/redis-access/scripts/redis_access.py --env DEV rpush mylist "value"

# Get list length
~/.claude/skills/redis-access/scripts/redis_access.py --env DEV llen mylist
```

### Set Operations

```bash
# Get set members
~/.claude/skills/redis-access/scripts/redis_access.py --env DEV smembers myset

# Add to set
~/.claude/skills/redis-access/scripts/redis_access.py --env DEV sadd myset "member"

# Remove from set
~/.claude/skills/redis-access/scripts/redis_access.py --env DEV srem myset "member"

# Check set membership
~/.claude/skills/redis-access/scripts/redis_access.py --env DEV sismember myset "member"
```

### Sorted Set Operations

```bash
# Get range by score
~/.claude/skills/redis-access/scripts/redis_access.py --env DEV zrange myzset 0 -1

# Add with score
~/.claude/skills/redis-access/scripts/redis_access.py --env DEV zadd myzset 1.0 "member"

# Get score
~/.claude/skills/redis-access/scripts/redis_access.py --env DEV zscore myzset "member"
```

### Server Information

```bash
# Get Redis server info
~/.claude/skills/redis-access/scripts/redis_access.py --env DEV info

# Get specific info section
~/.claude/skills/redis-access/scripts/redis_access.py --env DEV info --section memory

# Get database size
~/.claude/skills/redis-access/scripts/redis_access.py --env DEV dbsize

# Show connection config
~/.claude/skills/redis-access/scripts/redis_access.py --env DEV --show-config
```

## Safety Features

| Feature | Behavior |
|---------|----------|
| **Write Detection** | Detects SET, DEL, HSET, LPUSH, SADD, ZADD, FLUSHDB, FLUSHALL |
| **Confirmation** | Write operations require explicit confirmation |
| **PROD Protection** | PROD writes require typing "PROD" to confirm |
| **Dry Run** | Preview operations without executing with `--dry-run` |

## Output Formats

```bash
# Default (text)
~/.claude/skills/redis-access/scripts/redis_access.py --env DEV get mykey

# JSON output
~/.claude/skills/redis-access/scripts/redis_access.py --env DEV get mykey --format json

# Write to file
~/.claude/skills/redis-access/scripts/redis_access.py --env DEV hgetall myhash --output data.json --format json
```

## Workflow

### 1. Verify VPN Connectivity
- Read vpn-check skill
- Ensure VPN is connected for internal Redis instances
- Alternative: Skip if using localhost or public Redis

### 2. Configure Credentials
- Copy `.credentials.example` to `.credentials`
- Fill in environment-specific Redis connection details
- Ensure file permissions are 600

### 3. Execute Commands
- Use appropriate environment flag (--env DEV/QA/UAT/PROD)
- Review confirmations for write operations
- Use --dry-run for testing

## Exit Codes

- `0` = Success
- `1` = Error (connection failure, missing credentials, operation error)

## Examples

```bash
# Check if cache key exists in DEV
~/.claude/skills/redis-access/scripts/redis_access.py --env DEV exists session:user:123

# Get user session data
~/.claude/skills/redis-access/scripts/redis_access.py --env QA hgetall session:user:123

# List all rate limit keys
~/.claude/skills/redis-access/scripts/redis_access.py --env UAT keys "ratelimit:*"

# Clear a specific cache (with confirmation)
~/.claude/skills/redis-access/scripts/redis_access.py --env PROD del cache:products

# Get memory usage info
~/.claude/skills/redis-access/scripts/redis_access.py --env PROD info --section memory
```
