---
name: credential-setup
description: "Interactive credential setup helper. Automatically invoked when skills need credentials but .credentials file doesn't exist. Parses .credentials.example templates and prompts users for values. Use when: (1) A skill reports missing credentials, (2) User wants to set up credentials for a skill, (3) .credentials file needs to be created or regenerated."
---

# Credential Setup Helper

Automatically sets up credentials for skills by parsing `.credentials.example` templates and prompting for values.

## Core Philosophy

Security through separation: Credentials should never be committed to version control. This skill helps users create `.credentials` files from templates, ensuring a smooth setup experience while maintaining security best practices.

## Core Functionality

Parses `.credentials.example` templates and creates `.credentials` files through interactive prompts.

**What it does:**
1. Locates `.credentials.example` for the skill
2. Parses bash `export` statements to identify required variables
3. Prompts interactively for each credential (with password masking)
4. Creates `.credentials` file with proper permissions (600)
5. Validates against .gitignore patterns

## Usage

### Interactive Setup
```bash
# For specific skill (auto-finds .credentials.example)
python credential-setup/scripts/setup_credentials.py --skill bitbucket-repo-lookup

# Custom paths
python credential-setup/scripts/setup_credentials.py \
  --example path/to/.credentials.example \
  --output path/to/.credentials

# Preview without creating
python credential-setup/scripts/setup_credentials.py --skill my-skill --dry-run
```

### What Happens
1. Script locates or accepts `.credentials.example` template
2. Parses required variables from bash exports
3. Prompts for each credential with context and hints
4. Creates `.credentials` file with 600 permissions
5. Validates .gitignore coverage

## What Gets Created

**Input:** `.credentials.example`
```bash
# Option 1: App Password (Recommended)
export BITBUCKET_USERNAME="your-username-here"
export BITBUCKET_APP_PASSWORD="your-app-password-here"

# Option 2: Access Token
# export BITBUCKET_ACCESS_TOKEN="your-access-token-here"
```

**Interactive Prompts:**
```
Setting up credentials for bitbucket-repo-lookup...

Found 2 required credentials:

[Option 1: App Password (Recommended)]
BITBUCKET_USERNAME (hint: your-username-here): alice@example.com

[Option 1: App Password (Recommended)]
BITBUCKET_APP_PASSWORD (hint: your-app-password-here): ********

Optional credentials (currently commented):
- BITBUCKET_ACCESS_TOKEN

Enable optional credentials? [y/N]: n

Creating .credentials file...
✓ File created: bitbucket-repo-lookup/references/.credentials
✓ Permissions set to 600 (owner read/write only)
✓ Validated against .gitignore

Setup complete! To use these credentials:
  source bitbucket-repo-lookup/references/.credentials
```

**Output:** `.credentials`
```bash
# Bitbucket Credentials
# Created: 2026-01-05
# DO NOT commit this file - it's in .gitignore

# Option 1: App Password (Recommended)
export BITBUCKET_USERNAME="alice@example.com"
export BITBUCKET_APP_PASSWORD="ATBBxxxxxxxxxx"

# Option 2: Access Token
# export BITBUCKET_ACCESS_TOKEN="your-access-token-here"
```

## Features

### Smart Parsing

- **Extracts export statements**: Finds `export VAR="value"` patterns
- **Preserves context**: Includes comments above each variable for guidance
- **Handles optional credentials**: Recognizes commented-out exports as optional
- **Multi-option support**: Parses grouped credential sets (Option 1, Option 2, etc.)

### Interactive Experience

- **Clear prompts**: Shows context and hints for each credential
- **Secure input**: Uses password masking for sensitive values
- **Validation**: Ensures non-empty values for required credentials
- **Optional handling**: Asks whether to enable optional credential groups

### Security Features

- **File permissions**: Automatically sets to 600 (owner read/write only)
- **gitignore validation**: Warns if .credentials isn't in .gitignore
- **No echoing**: Credentials never printed to terminal
- **Backup option**: Optionally backs up existing .credentials before overwriting

### Flexible Usage

- **Auto-discovery**: `--skill name` finds the .credentials.example automatically
- **Custom paths**: Specify exact `--example` and `--output` locations
- **Dry run**: Preview what would be created without actually creating it
- **Non-interactive**: Support for scripted setups (future)

## Integration Pattern

For skills requiring credentials, declare credential-setup as a dependency:

### 1. Create `.credentials.example`

Place in `your-skill/references/.credentials.example`:
```bash
# [Your Skill] Credentials
export API_KEY="your-api-key-here"
export API_URL="https://api.example.com"
```

### 2. Declare Dependency in SKILL.md

```markdown
## Dependencies

| Skill | Path | Purpose |
|-------|------|---------|
| credential-setup | `credential-setup/SKILL.md` | Configure [Service] credentials |

## Workflow

### 1. Authenticate
- Read credential-setup skill
- Ensure .credentials exists for [Service] access
```

### 3. Reference in Workflow Steps

Integrate credential setup as a workflow step, not a prerequisite:
- "Read credential-setup skill"
- "Ensure .credentials file exists"
- No claims about automatic behavior

See `references/usage-guide.md` for detailed integration examples.

## Command Reference

### Basic Usage

```bash
# Auto-discover .credentials.example for a skill
python credential-setup/scripts/setup_credentials.py --skill SKILL_NAME

# Specify exact paths
python credential-setup/scripts/setup_credentials.py \
  --example PATH/TO/.credentials.example \
  --output PATH/TO/.credentials
```

### Options

| Flag | Description |
|------|-------------|
| `--skill NAME` | Skill name (auto-finds .credentials.example in skill/references/) |
| `--example PATH` | Path to .credentials.example template |
| `--output PATH` | Output path for .credentials file |
| `--dry-run` | Show what would be created without creating it |
| `--backup` | Backup existing .credentials before overwriting |
| `--help` | Show help message |

### Examples

```bash
# Setup for bitbucket-repo-lookup
python credential-setup/scripts/setup_credentials.py --skill bitbucket-repo-lookup

# Preview what would be created
python credential-setup/scripts/setup_credentials.py --skill bitbucket-repo-lookup --dry-run

# Custom template location
python credential-setup/scripts/setup_credentials.py \
  --example ~/custom/.credentials.example \
  --output ~/custom/.credentials

# With backup of existing file
python credential-setup/scripts/setup_credentials.py --skill bitbucket-repo-lookup --backup
```

## Troubleshooting

### Template Not Found

**Error:** `FileNotFoundError: .credentials.example not found`

**Solution:**
1. Verify the skill has a `.credentials.example` in its `references/` directory
2. Use `--example` to specify the exact path
3. Create `.credentials.example` if it doesn't exist (see skill-creator/references/credential-patterns.md)

### Permission Denied

**Error:** `PermissionError: Cannot write to .credentials`

**Solution:**
1. Check directory permissions: `ls -la skill/references/`
2. Ensure you have write access to the directory
3. Try with appropriate permissions or different output location

### File Already Exists

**Behavior:** Script asks for confirmation before overwriting

**Options:**
- Confirm to overwrite existing .credentials
- Cancel and manually backup the file first
- Use `--backup` flag to automatically backup before overwriting

### gitignore Warning

**Warning:** `.credentials not found in .gitignore`

**Solution:**
1. Add `.credentials` to your repository's `.gitignore`:
   ```gitignore
   # Credentials (NEVER commit these)
   .credentials
   **/references/.credentials
   ```
2. Verify with: `git check-ignore .credentials` (should be ignored)

## Security Best Practices

1. **Never commit .credentials** - Always in .gitignore
2. **File permissions** - Automatically set to 600 (owner only)
3. **Review before sourcing** - Check file contents before `source .credentials`
4. **Rotate regularly** - Update credentials periodically
5. **Use app passwords** - More secure than account passwords where available
6. **Audit access** - Review which skills have credentials

## Related Resources

- `references/usage-guide.md` - Detailed integration guide for skill developers
- `skill-creator/references/credential-patterns.md` - Credential management patterns
- `bitbucket-repo-lookup/` - Reference implementation example
