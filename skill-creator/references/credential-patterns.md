# Credential Management Patterns for Skills

When creating skills that require API credentials, tokens, or other sensitive data, follow these patterns to prevent accidental commits and ensure security.

## Core Principle

**Never commit credentials to version control.** Separate configuration (workspace settings, paths, preferences) from credentials (passwords, tokens, API keys).

---

## Recommended Pattern: Credentials File + Template

This is the **recommended approach** for skills that need authentication.

### Structure

```
your-skill/
├── SKILL.md
├── references/
│   ├── config.md                    # Non-sensitive configuration (checked in)
│   └── .credentials.example         # Template (checked in, safe)
└── scripts/
    └── your_script.py               # Reads from environment variables
```

User creates locally (NOT checked in):
```
references/.credentials              # User's actual credentials (in .gitignore)
```

### Implementation

#### 1. Create `.credentials.example` Template

**File:** `references/.credentials.example`

```bash
# [Skill Name] Credentials Template
#
# SECURITY: This is a template. Copy to .credentials and fill in actual values.
# DO NOT commit .credentials - it's in .gitignore
#
# Setup:
#   1. cp .credentials.example .credentials
#   2. Edit .credentials with your actual credentials
#   3. source your-skill/references/.credentials
#   4. Run your script

# ============================================================================
# Option 1: API Key (Most Common)
# ============================================================================
export API_SERVICE_KEY="your-api-key-here"
export API_SERVICE_URL="https://api.example.com"

# ============================================================================
# Option 2: Username/Password
# ============================================================================
# export SERVICE_USERNAME="your-username"
# export SERVICE_PASSWORD="your-password"

# ============================================================================
# Verification
# ============================================================================
# After sourcing, verify:
#   echo $API_SERVICE_KEY
```

#### 2. Update `.gitignore`

Add to the **project root** `.gitignore`:

```gitignore
# Credentials (NEVER commit these)
.credentials
**/references/.credentials
your-skill/references/.credentials
```

#### 3. Update `config.md`

**File:** `references/config.md`

```markdown
# [Skill Name] Configuration

## Authentication

**Credentials are stored separately for security.**

See `.credentials.example` for setup. Recommended approach:

1. Copy the template:
   ```bash
   cp your-skill/references/.credentials.example your-skill/references/.credentials
   ```

2. Edit `.credentials` with your actual credentials

3. Source before using:
   ```bash
   source your-skill/references/.credentials
   ```

## Service Configuration

```yaml
api:
  base_url: https://api.example.com
  timeout: 30
  retry_count: 3
```
```

#### 4. Python Script Pattern

**File:** `scripts/your_script.py`

```python
#!/usr/bin/env python3
import os
import sys

# Read from environment variables
API_KEY = os.getenv("API_SERVICE_KEY")
API_URL = os.getenv("API_SERVICE_URL", "https://api.example.com")

if not API_KEY:
    print("Error: API_SERVICE_KEY not set")
    print("Source credentials: source your-skill/references/.credentials")
    sys.exit(1)

# Use the credentials
headers = {"Authorization": f"Bearer {API_KEY}"}
```

#### 5. Document in SKILL.md

Add to your skill's Quick Start section:

```markdown
## Quick Start

### 1. Set Up Credentials

```bash
# Copy the credentials template
cp your-skill/references/.credentials.example your-skill/references/.credentials

# Edit .credentials with your actual API key
# Then source it
source your-skill/references/.credentials
```

### 2. Configure Settings

Edit `references/config.md` for non-sensitive settings like URLs, timeouts, etc.
```

---

## Alternative Pattern: Environment Variables Only

For simpler skills or cross-project credentials, use environment variables without a credentials file.

### Implementation

#### 1. Document in SKILL.md

```markdown
## Authentication

Set these environment variables:

```bash
# Add to ~/.bashrc or ~/.zshrc
export SERVICE_API_KEY="your-api-key"
export SERVICE_BASE_URL="https://api.example.com"
```

Verify:
```bash
echo $SERVICE_API_KEY
```
```

#### 2. Python Script

```python
#!/usr/bin/env python3
import os
import sys

API_KEY = os.getenv("SERVICE_API_KEY")
if not API_KEY:
    print("Error: SERVICE_API_KEY environment variable not set")
    print("Set it with: export SERVICE_API_KEY='your-key'")
    sys.exit(1)
```

**Pros:**
- ✅ Simple setup
- ✅ Works across all projects
- ✅ No files to manage

**Cons:**
- ❌ Less convenient for project-specific credentials
- ❌ No template to guide users
- ❌ Credentials shared across all projects

---

## Three-Tier Strategy (Most Flexible)

For maximum flexibility, support all three methods in priority order.

### Authentication Priority

1. **Environment variables** (checked first)
2. **Credentials file** (checked second)
3. **CLI arguments** (fallback for one-time use)

### Python Implementation

```python
#!/usr/bin/env python3
import os
import argparse
from pathlib import Path

def get_credentials():
    """Get credentials from env vars, file, or CLI args (in that order)."""

    # Priority 1: Environment variables
    api_key = os.getenv("SERVICE_API_KEY")
    if api_key:
        return {"api_key": api_key, "source": "environment"}

    # Priority 2: Credentials file
    creds_file = Path(__file__).parent.parent / "references" / ".credentials"
    if creds_file.exists():
        # Source the file and read env vars
        # (In practice, user sources it before running)
        pass

    # Priority 3: CLI arguments (handled by argparse)
    return {"api_key": None, "source": "none"}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--api-key", help="API key (or use $SERVICE_API_KEY)")
    args = parser.parse_args()

    creds = get_credentials()
    api_key = args.api_key or creds["api_key"]

    if not api_key:
        print("Error: No API key provided")
        print("Options:")
        print("  1. Set environment: export SERVICE_API_KEY='your-key'")
        print("  2. Use credentials file: source references/.credentials")
        print("  3. Pass as argument: --api-key YOUR_KEY")
        sys.exit(1)

    print(f"Using credentials from: {creds['source'] if not args.api_key else 'CLI'}")
```

### Documentation

```markdown
## Authentication

Choose one method:

**Option A: Environment Variables (Recommended for permanent setup)**
```bash
export SERVICE_API_KEY="your-api-key"
```

**Option B: Credentials File (Convenient for project-specific)**
```bash
cp references/.credentials.example references/.credentials
# Edit .credentials
source references/.credentials
```

**Option C: CLI Arguments (One-time use)**
```bash
python scripts/script.py --api-key YOUR_KEY
```
```

---

## Security Checklist

When implementing credential management:

- [ ] `.credentials` added to `.gitignore`
- [ ] `.credentials.example` created with placeholder values
- [ ] No real credentials in any checked-in files
- [ ] Documentation shows all authentication methods
- [ ] Scripts validate credentials before use
- [ ] Error messages guide users to setup docs
- [ ] Security notes in README.md updated

---

## Real-World Example: bitbucket-repo-lookup

See the `bitbucket-repo-lookup` skill for a complete implementation:

```
bitbucket-repo-lookup/
├── references/
│   ├── .credentials.example         # Template with instructions
│   └── config.md                    # Non-sensitive config only
└── scripts/
    └── bitbucket_api.py             # Reads BITBUCKET_USERNAME, BITBUCKET_APP_PASSWORD
```

**Features:**
- ✅ Three authentication methods (env vars, file, CLI)
- ✅ Clear setup instructions in `.credentials.example`
- ✅ Comprehensive error messages
- ✅ Security notes in README.md

---

## Anti-Patterns to Avoid

❌ **Don't:** Put credentials directly in `config.md`
```markdown
# Bad - credentials mixed with config
api_key: sk-1234567890abcdef
base_url: https://api.example.com
```

❌ **Don't:** Use `.env` files without `.gitignore`
```bash
# Bad - .env often gets committed accidentally
API_KEY=sk-1234567890abcdef
```

❌ **Don't:** Hardcode credentials in scripts
```python
# Bad - credentials in code
API_KEY = "sk-1234567890abcdef"
```

❌ **Don't:** Rely on "don't commit" warnings alone
```markdown
# Bad - no enforcement
# WARNING: Don't commit this file with real credentials!
api_key: your-key-here
```

✅ **Do:** Physically separate credentials from configuration
✅ **Do:** Use `.gitignore` to prevent commits
✅ **Do:** Provide templates with placeholders
✅ **Do:** Support multiple authentication methods
✅ **Do:** Validate credentials before use
✅ **Do:** Guide users with clear error messages

---

## Quick Reference

| Pattern | Use When | Pros | Cons |
|---------|----------|------|------|
| **Credentials File + Template** | Most skills | ✅ Secure<br>✅ Guided setup<br>✅ Project-specific | ❌ Extra file to manage |
| **Environment Variables Only** | Simple/cross-project | ✅ Simple<br>✅ Cross-project | ❌ No template<br>❌ Shared everywhere |
| **Three-Tier Strategy** | Complex integrations | ✅ Maximum flexibility<br>✅ Multiple use cases | ❌ More code<br>❌ More documentation |

**Recommendation:** Use **Credentials File + Template** for most skills. It balances security, usability, and developer experience.
