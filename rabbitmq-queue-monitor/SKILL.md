---
name: rabbitmq-queue-monitor
description: "Monitor RabbitMQ queues and health across LOCAL/DEV/QA/UAT/PROD environments with message counts, consumer status, and server health checks"
version: 1.0.0
author: David Rutgos
---

# RabbitMQ Queue Monitor Skill

Monitor RabbitMQ queues and server health across LOCAL/DEV/QA/UAT/PROD environments.

## Purpose

Enable quick RabbitMQ monitoring from the command line with:
- Multi-environment support (LOCAL, DEV, QA, UAT, PROD)
- Queue message counts and consumer status
- Server health and node status
- Connection and channel monitoring
- Credential auto-loading from `.credentials` file

## Dependencies

| Skill | Path | Purpose |
|-------|------|---------|
| vpn-check | `vpn-check/SKILL.md` | Verify VPN connectivity before accessing internal RabbitMQ instances |

## One-Time Setup

```bash
cd ~/.claude/skills/rabbitmq-queue-monitor && bash setup.sh
```

This creates a virtual environment and installs the `requests` Python package.

## Configuration

Copy the example credentials file and fill in your values:

```bash
cp references/.credentials.example references/.credentials
chmod 600 references/.credentials
```

### Credentials Format

```bash
# LOCAL Environment
export RABBITMQ_LOCAL_HOST="localhost"
export RABBITMQ_LOCAL_PORT="15672"
export RABBITMQ_LOCAL_USERNAME="guest"
export RABBITMQ_LOCAL_PASSWORD="guest"
export RABBITMQ_LOCAL_VHOST="/"

# DEV Environment
export RABBITMQ_DEV_HOST="rabbitmq-dev.internal.example.com"
export RABBITMQ_DEV_PORT="15672"
export RABBITMQ_DEV_USERNAME="admin"
export RABBITMQ_DEV_PASSWORD="your-password"
export RABBITMQ_DEV_VHOST="/"

# QA Environment
export RABBITMQ_QA_HOST="rabbitmq-qa.internal.example.com"
export RABBITMQ_QA_PORT="15672"
export RABBITMQ_QA_USERNAME="admin"
export RABBITMQ_QA_PASSWORD="your-password"
export RABBITMQ_QA_VHOST="/"

# UAT Environment
export RABBITMQ_UAT_HOST="rabbitmq-uat.internal.example.com"
export RABBITMQ_UAT_PORT="15672"
export RABBITMQ_UAT_USERNAME="admin"
export RABBITMQ_UAT_PASSWORD="your-password"
export RABBITMQ_UAT_VHOST="/"

# PROD Environment
export RABBITMQ_PROD_HOST="rabbitmq-prod.internal.example.com"
export RABBITMQ_PROD_PORT="15672"
export RABBITMQ_PROD_USERNAME="admin"
export RABBITMQ_PROD_PASSWORD="your-password"
export RABBITMQ_PROD_VHOST="/"
```

## Usage

### Health and Overview

```bash
# Get RabbitMQ server overview (version, cluster, totals)
~/.claude/skills/rabbitmq-queue-monitor/scripts/rabbitmq_monitor.py --env DEV overview

# Check node health
~/.claude/skills/rabbitmq-queue-monitor/scripts/rabbitmq_monitor.py --env DEV nodes

# Get health check status
~/.claude/skills/rabbitmq-queue-monitor/scripts/rabbitmq_monitor.py --env DEV health
```

### Queue Operations

```bash
# List all queues with message counts
~/.claude/skills/rabbitmq-queue-monitor/scripts/rabbitmq_monitor.py --env DEV queues

# List queues with messages > 0 (backlog)
~/.claude/skills/rabbitmq-queue-monitor/scripts/rabbitmq_monitor.py --env DEV queues --backlog

# Filter queues by name pattern
~/.claude/skills/rabbitmq-queue-monitor/scripts/rabbitmq_monitor.py --env DEV queues --filter "order"

# Get detailed info for a specific queue
~/.claude/skills/rabbitmq-queue-monitor/scripts/rabbitmq_monitor.py --env DEV queue my-queue-name

# Get queue message rates
~/.claude/skills/rabbitmq-queue-monitor/scripts/rabbitmq_monitor.py --env DEV queue my-queue-name --rates
```

### Connection and Channel Monitoring

```bash
# List all connections
~/.claude/skills/rabbitmq-queue-monitor/scripts/rabbitmq_monitor.py --env DEV connections

# List all channels
~/.claude/skills/rabbitmq-queue-monitor/scripts/rabbitmq_monitor.py --env DEV channels

# List consumers
~/.claude/skills/rabbitmq-queue-monitor/scripts/rabbitmq_monitor.py --env DEV consumers
```

### Exchange and Binding Info

```bash
# List exchanges
~/.claude/skills/rabbitmq-queue-monitor/scripts/rabbitmq_monitor.py --env DEV exchanges

# List bindings for a queue
~/.claude/skills/rabbitmq-queue-monitor/scripts/rabbitmq_monitor.py --env DEV bindings my-queue-name
```

## Output Formats

```bash
# Default (text/table)
~/.claude/skills/rabbitmq-queue-monitor/scripts/rabbitmq_monitor.py --env DEV queues

# JSON output
~/.claude/skills/rabbitmq-queue-monitor/scripts/rabbitmq_monitor.py --env DEV queues --format json

# Write to file
~/.claude/skills/rabbitmq-queue-monitor/scripts/rabbitmq_monitor.py --env DEV queues --output queues.json --format json
```

## Common Use Cases

### Check for Message Backlog

```bash
# Quick check for queues with pending messages
~/.claude/skills/rabbitmq-queue-monitor/scripts/rabbitmq_monitor.py --env PROD queues --backlog
```

### Monitor Specific Queue

```bash
# Get detailed queue info including message rates
~/.claude/skills/rabbitmq-queue-monitor/scripts/rabbitmq_monitor.py --env UAT queue order-processing --rates
```

### Health Check Before Deployment

```bash
# Verify RabbitMQ is healthy before deploying
~/.claude/skills/rabbitmq-queue-monitor/scripts/rabbitmq_monitor.py --env PROD health
~/.claude/skills/rabbitmq-queue-monitor/scripts/rabbitmq_monitor.py --env PROD nodes
```

### Find Queues Without Consumers

```bash
# List all queues and look for consumer_count = 0
~/.claude/skills/rabbitmq-queue-monitor/scripts/rabbitmq_monitor.py --env QA queues --format json | jq '.[] | select(.consumers == 0)'
```

## Workflow

### 1. Verify VPN Connectivity
- Read vpn-check skill
- Ensure VPN is connected for internal RabbitMQ instances
- Alternative: Skip if using localhost

### 2. Configure Credentials
- Copy `.credentials.example` to `.credentials`
- Fill in environment-specific RabbitMQ Management API details
- Ensure file permissions are 600

### 3. Monitor Queues
- Use appropriate environment flag (--env LOCAL/DEV/QA/UAT/PROD)
- Check queue message counts and consumer status
- Monitor health before/after deployments

## Exit Codes

- `0` = Success
- `1` = Error (connection failure, missing credentials, operation error)

## Examples

```bash
# Quick health check
~/.claude/skills/rabbitmq-queue-monitor/scripts/rabbitmq_monitor.py --env DEV health

# Find queues with message backlog in production
~/.claude/skills/rabbitmq-queue-monitor/scripts/rabbitmq_monitor.py --env PROD queues --backlog

# Get detailed queue info
~/.claude/skills/rabbitmq-queue-monitor/scripts/rabbitmq_monitor.py --env QA queue email-notifications

# Export all queue data to JSON
~/.claude/skills/rabbitmq-queue-monitor/scripts/rabbitmq_monitor.py --env UAT queues --format json --output /tmp/queues.json

# Show connection configuration
~/.claude/skills/rabbitmq-queue-monitor/scripts/rabbitmq_monitor.py --env DEV --show-config
```

## Notes

- Uses the RabbitMQ Management HTTP API (default port 15672)
- Requires the RabbitMQ Management plugin to be enabled
- All operations are read-only (no queue modifications)
- SSL/TLS is supported via RABBITMQ_{ENV}_SSL="true"
