---
name: vpn-check
description: "Check VPN connectivity by verifying internal DNS resolution. Use standalone to verify VPN status, or as a prerequisite for skills requiring internal network access (e.g., bitbucket-repo-lookup). Auto-prompts for configuration on first run."
---

# VPN Check

Verifies VPN connectivity by checking if internal hostnames resolve via DNS.

## Core Functionality

The skill performs a DNS lookup on an internal hostname that only resolves when connected to VPN:
- **Connected**: Hostname resolves to an IP address
- **Not Connected**: DNS lookup fails with "unknown host"

This is the fastest and most reliable way to detect VPN status without requiring authentication or service availability.

## First Run Setup

On first run (or with `--setup`), the skill prompts for configuration:

```
VPN Check - First Time Setup
============================================================

This skill checks VPN connectivity by verifying that internal
hostnames can be resolved via DNS.

Internal hostname to check (e.g., internal.example.com): internal.yourcompany.com

Optional: Expected IP address for extra validation
  Leave empty to skip (any resolved IP will be accepted)
Expected IP address: 172.16.140.176

Config created: ~/.claude/skills/vpn-check/.vpn-config
```

Configuration is stored in `~/.claude/skills/vpn-check/.vpn-config` (never committed to git).

## Usage

### Standalone Check

```bash
# Check VPN status
python vpn-check/scripts/check_vpn.py

# Quiet mode (exit code only, for scripting)
python vpn-check/scripts/check_vpn.py --quiet

# Force re-run setup
python vpn-check/scripts/check_vpn.py --setup

# Custom timeout
python vpn-check/scripts/check_vpn.py --timeout 10
```

### Skill Stacking

Other skills can use vpn-check as a prerequisite. Add to your skill's workflow:

```markdown
## Workflow

### 1. Verify Network Access
- Run vpn-check to verify VPN connectivity
- If not connected, prompt user to connect before proceeding
```

Or call programmatically:

```python
import subprocess

def check_vpn_prerequisite():
    """Verify VPN before proceeding."""
    result = subprocess.run(
        ['python3', 'vpn-check/scripts/check_vpn.py', '--quiet'],
        capture_output=True
    )
    if result.returncode != 0:
        print("VPN not connected. Please connect and try again.")
        return False
    return True
```

## Exit Codes

| Code | Meaning | Action |
|------|---------|--------|
| 0 | VPN connected | Proceed with VPN-dependent operations |
| 1 | VPN not connected | Prompt user to connect |
| 2 | Configuration error | Run `--setup` to reconfigure |

## Example Output

**Connected:**
```
VPN Connected
  Host: internal.yourcompany.com
  IP: 172.16.140.176
```

**Not Connected:**
```
VPN Not Connected
  Could not resolve: internal.yourcompany.com

  Please connect to your VPN and try again.
```

## Configuration Options

The `.vpn-config` file supports these settings:

| Variable | Required | Description |
|----------|----------|-------------|
| `VPN_CHECK_HOST` | Yes | Internal hostname to check |
| `VPN_CHECK_EXPECTED_IP` | No | Expected IP for extra validation |
| `VPN_CHECK_TIMEOUT` | No | DNS timeout in seconds (default: 5) |
| `VPN_CHECK_FALLBACK_HOSTS` | No | Comma-separated backup hosts |

Example config:
```bash
export VPN_CHECK_HOST="internal.yourcompany.com"
export VPN_CHECK_EXPECTED_IP="172.16.140.176"
export VPN_CHECK_TIMEOUT="5"
```

## Troubleshooting

### Config Not Found

```
No VPN configuration found.
```

**Solution:** Run setup with `python vpn-check/scripts/check_vpn.py --setup`

### Wrong IP Resolved

```
VPN Status: UNEXPECTED IP
  Host: internal.example.com
  Got IP: 192.168.1.1
  Expected: 10.0.0.1
```

**Cause:** Connected to wrong network (e.g., home WiFi resolving to local DNS)
**Solution:** Connect to correct VPN

### Timeout

```
VPN Not Connected
  DNS lookup timed out: internal.example.com
```

**Cause:** Network issues or firewall blocking DNS
**Solution:** Check network connection, increase timeout with `--timeout`

## Security

- Config file stored in `~/.claude/skills/vpn-check/.vpn-config` with 600 permissions
- Internal hostnames never committed to git
- No credentials required - DNS resolution only
