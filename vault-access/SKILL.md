---
name: vault-access
description: "Retrieve secrets from HashiCorp Vault. Supports KV v1/v2 engines, token authentication, and multiple paths. Use when user needs to fetch credentials, API keys, or other secrets stored in Vault. Requires VPN connectivity for internal Vault servers."
version: 1.0.0
---

# Vault Access

Retrieve secrets from HashiCorp Vault with environment-aware configuration.

## Key Behavior

**Authentication**: Uses Vault token authentication (most common method).

**KV Engine Detection**: Automatically detects KV v1 vs v2 based on response or explicit configuration.

**Secret Paths**: Supports both direct paths and paths with keys for specific values.

## Prerequisites

### Stacked Skills
- **vpn-check** — Run `/vpn-check` before accessing internal Vault (often required)
- **credential-setup** — Run `/credential-setup vault-access` if `.credentials` missing

### Dependencies

Requires the `requests` library:
```bash
pip install requests
```

---

## Workflow

### Step 1: Verify VPN (if internal Vault)
```bash
python ~/.claude/skills/vpn-check/scripts/check_vpn.py --quiet
```

### Step 2: Load Credentials
```bash
cat ~/.claude/skills/vault-access/references/.credentials
```
If missing, invoke `/credential-setup vault-access`.

### Step 3: Retrieve Secret
```bash
python vault-access/scripts/vault_access.py get secret/myapp/database
```

### Step 4: Return Results
- **Single key**: Return the value directly
- **Full secret**: Return as key-value pairs (masked by default)
- **Errors**: Show error with suggestions

---

## Script Usage

```bash
# Get all key-value pairs from a secret path
python vault-access/scripts/vault_access.py get secret/myapp/database

# Get a specific key from a secret
python vault-access/scripts/vault_access.py get secret/myapp/database --key password

# List secrets in a path
python vault-access/scripts/vault_access.py list secret/myapp/

# Show values (unmask secrets)
python vault-access/scripts/vault_access.py get secret/myapp/database --show

# Export as environment variables format
python vault-access/scripts/vault_access.py get secret/myapp/database --format env

# Specify KV version explicitly
python vault-access/scripts/vault_access.py get secret/myapp/database --kv-version 2

# Check Vault connectivity
python vault-access/scripts/vault_access.py status
```

### Arguments

| Argument | Description |
|----------|-------------|
| `get <path>` | Retrieve secret(s) from path |
| `list <path>` | List secrets in a path |
| `status` | Check Vault connectivity and auth status |
| `--key`, `-k` | Get specific key from secret |
| `--show`, `-s` | Show actual values (default: masked) |
| `--format`, `-f` | Output: table (default), json, env, raw |
| `--kv-version` | Force KV version: 1 or 2 (default: auto-detect) |
| `--output`, `-o` | Write output to file |

---

## Examples

### Retrieve Database Credentials
```
User: Get the database password from Vault

Claude:
1. VPN check: connected
2. Path: secret/myapp/database
3. Execute: vault_access.py get secret/myapp/database --key password
4. Return masked value or show if user requests
```

### List Available Secrets
```
User: What secrets are available under secret/myapp?

Claude:
1. VPN check: connected
2. Execute: vault_access.py list secret/myapp/
3. Return list of secret paths
```

### Export for Shell
```
User: Export the API credentials for my script

Claude:
1. VPN check: connected
2. Execute: vault_access.py get secret/myapp/api --format env
3. Return:
   export API_KEY="***"
   export API_SECRET="***"
```

---

## Edge Cases

| Case | Handling |
|------|----------|
| Path not found | Show error, suggest checking path |
| Permission denied | Check token permissions, suggest renewing |
| Vault sealed | Prompt to unseal or contact admin |
| Token expired | Prompt to refresh token |
| KV version mismatch | Auto-retry with other version |
| Missing credentials | Prompt to run `/credential-setup` |
| VPN not connected | Suggest connecting to VPN |

---

## KV Engine Versions

HashiCorp Vault has two KV (Key-Value) engine versions:

### KV v1
- Simple key-value storage
- Path: `secret/myapp/database`
- API: `GET /v1/secret/myapp/database`

### KV v2 (Default in modern Vault)
- Versioned secrets with metadata
- Path: `secret/myapp/database`
- API: `GET /v1/secret/data/myapp/database`
- Data nested under `.data.data` in response

**Auto-detection**: The script first tries v2 format, falls back to v1 if that fails.

---

## Configuration

### Credential Structure
```
VAULT_ADDR      - Vault server URL (required)
VAULT_TOKEN     - Authentication token (required)
VAULT_NAMESPACE - Enterprise namespace (optional)
VAULT_SKIP_VERIFY - Skip TLS verification (optional, not recommended)
```

### First-Time Setup
```bash
cd vault-access/references
cp .credentials.example .credentials
# Edit .credentials with your values
chmod 600 .credentials  # Secure permissions
```

### Getting a Vault Token

**From Vault CLI:**
```bash
vault login -method=ldap username=youruser
vault token create -ttl=8h
```

**From Web UI:**
1. Log into Vault UI
2. Click user icon > Copy Token

**Service accounts:**
Contact your Vault administrator for AppRole or other service authentication.

---

## Security

- **Token security**: Tokens should have minimum required permissions
- **Short TTL**: Use tokens with short time-to-live when possible
- **Never log secrets**: Values are masked by default
- **File permissions**: `.credentials` should be 600 (owner read/write only)
- **VPN required**: Internal Vault servers typically require VPN
