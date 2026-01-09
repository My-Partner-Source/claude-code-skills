---
name: datadog-api
description: "Query Datadog metrics, monitors, dashboards, and events. Use when you need to check application health, view alert status, query time-series metrics, or investigate incidents. Supports multiple Datadog sites (US, EU, etc.)."
version: 1.0.0
---

# Datadog API

Access Datadog monitoring data including metrics, monitors, dashboards, and events.

## Core Philosophy

This skill provides read-only access to your Datadog observability data. Instead of switching to the Datadog web UI, query metrics, check alert status, and investigate incidents directly from your development environment.

## Key Behavior

**Read-Only Operations**: This skill focuses on querying data, not modifying configurations:
- Query time-series metrics
- List and check monitor/alert status
- View dashboard definitions
- Search events and logs

**Site Selection**: Datadog has multiple regional sites. The script auto-detects based on your API key or you can specify explicitly.

## Dependencies

| Skill | Path | Purpose |
|-------|------|---------|
| credential-setup | `credential-setup/SKILL.md` | Configure Datadog API credentials |

## Workflow

### 1. Configure Credentials
- Read credential-setup skill
- Ensure `.credentials` exists with `DD_API_KEY` and `DD_APP_KEY`
- Alternative: Set environment variables

### 2. Query Data
Use natural language queries to access Datadog:
- "Show me the monitors that are currently alerting"
- "Query the CPU usage metric for prod-web-01 over the last hour"
- "List all dashboards containing 'production'"
- "Get recent events tagged with 'service:api'"

## Commands

### List Monitors
```bash
python datadog-api/scripts/datadog_api.py monitors [--status alerting|warn|ok|all] [--tag TAG]
```

Show monitor status with optional filtering:
- `--status alerting` - Only monitors currently in alert state
- `--status warn` - Monitors in warning state
- `--tag service:api` - Filter by tag

### Query Metrics
```bash
python datadog-api/scripts/datadog_api.py query --metric METRIC [--from HOURS_AGO] [--tags TAGS]
```

Query time-series metrics:
- `--metric system.cpu.user` - The metric name to query
- `--from 1` - Hours ago to start (default: 1)
- `--tags host:prod-web-01` - Filter by tags

### List Dashboards
```bash
python datadog-api/scripts/datadog_api.py dashboards [--filter NAME]
```

List available dashboards with optional name filter.

### Get Events
```bash
python datadog-api/scripts/datadog_api.py events [--from HOURS_AGO] [--tags TAGS] [--priority normal|low]
```

Search recent events:
- `--from 24` - Hours ago to search (default: 24)
- `--tags service:api` - Filter by tags
- `--priority normal` - Filter by priority

### Check Monitor Details
```bash
python datadog-api/scripts/datadog_api.py monitor-info --id MONITOR_ID
```

Get detailed information about a specific monitor.

### Get Dashboard Definition
```bash
python datadog-api/scripts/datadog_api.py dashboard-info --id DASHBOARD_ID
```

Get the definition of a specific dashboard.

## Examples

### Check Production Health
```
User: Are there any alerts firing right now?

Claude:
1. Loads credentials
2. Runs: datadog_api.py monitors --status alerting
3. Returns formatted alert list with status and message
```

### Investigate High CPU
```
User: What's the CPU usage on prod-web-01 over the last 2 hours?

Claude:
1. Runs: datadog_api.py query --metric system.cpu.user --from 2 --tags host:prod-web-01
2. Returns time-series data with min/max/avg summary
```

### Review Recent Incidents
```
User: Show me any deployment events from today

Claude:
1. Runs: datadog_api.py events --from 24 --tags source:deploy
2. Returns list of deployment events with timestamps
```

## Output Formats

### Monitors List
```
┌────────────────────────────────────────────────────────────────────────────┐
│ Status │ Name                          │ Type    │ Last Triggered         │
├────────────────────────────────────────────────────────────────────────────┤
│ Alert  │ High CPU on Production        │ metric  │ 2026-01-09 10:23:45    │
│ OK     │ API Response Time             │ metric  │ 2026-01-08 15:00:00    │
│ Warn   │ Disk Space Low                │ metric  │ 2026-01-09 09:45:00    │
└────────────────────────────────────────────────────────────────────────────┘
```

### Metrics Query
```
Metric: system.cpu.user
Host: prod-web-01
Time Range: 2026-01-09 09:00 to 2026-01-09 11:00

Summary:
  Min: 12.3%
  Max: 87.5%
  Avg: 45.2%

Data Points: 120
```

## Configuration

### Datadog Sites

| Site | API Base URL | Region |
|------|-------------|--------|
| US1 (default) | `https://api.datadoghq.com` | United States |
| US3 | `https://api.us3.datadoghq.com` | United States |
| US5 | `https://api.us5.datadoghq.com` | United States |
| EU1 | `https://api.datadoghq.eu` | Europe |
| AP1 | `https://api.ap1.datadoghq.com` | Asia Pacific |
| GOV | `https://api.ddog-gov.com` | US Government |

### Credential Structure
```
DD_API_KEY     - Datadog API key (required)
DD_APP_KEY     - Datadog Application key (required)
DD_SITE        - Datadog site (optional, default: datadoghq.com)
```

### First-Time Setup
```bash
cd datadog-api/references
cp .credentials.example .credentials
# Edit .credentials with your values
chmod 600 .credentials  # Secure permissions
```

Or use the credential-setup skill:
```bash
python credential-setup/scripts/setup_credentials.py --skill datadog-api
```

## Reference Files

- **references/.credentials.example** - Credential template
- **scripts/datadog_api.py** - Python API wrapper

## Security Notes

- **Read-only access** - This skill doesn't modify Datadog configurations
- **Never commit credentials** - Keep `.credentials` in `.gitignore`
- **Use scoped keys** - Create API/App keys with minimal required permissions
- **Key rotation** - Rotate your keys regularly

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Authentication failed | Verify API and App keys are correct |
| 403 Forbidden | Check key permissions in Datadog settings |
| Wrong data/site | Verify DD_SITE matches your Datadog account region |
| Rate limited | Wait and retry, reduce query frequency |
| No data returned | Check metric name and tag filters |

## API Limits

- **Rate limiting**: 300 requests/hour for free tier, higher for paid
- **Query time range**: Maximum 24 hours per query for detailed metrics
- **Pagination**: Results paginated at 100 items per page
