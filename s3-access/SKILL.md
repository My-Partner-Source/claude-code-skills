---
name: s3-access
description: "Access Amazon S3 buckets and objects. List buckets, browse objects, upload/download files, and get object metadata. Supports multiple AWS profiles and regions. Use when user needs to interact with S3 storage."
version: 1.0.0
---

# S3 Access

Access Amazon S3 buckets and objects with environment-aware configuration.

## Key Behavior

**Authentication**: Uses AWS credentials (access key/secret key) or AWS profiles.

**Region Support**: Supports all AWS regions with configurable defaults.

**Operations**: List buckets, list objects, get/put objects, get metadata.

## Prerequisites

### Stacked Skills
- **vpn-check** — Run `/vpn-check` before accessing S3 via VPN endpoint (if required)
- **credential-setup** — Run `/credential-setup s3-access` if `.credentials` missing

### Dependencies

**One-time setup** (creates virtual environment and installs boto3):

```bash
cd ~/.claude/skills/s3-access && bash setup.sh
```

This creates a `.venv` folder and configures the script to use it automatically.

---

## Workflow

### Step 1: Verify VPN (if using VPC endpoint)
```bash
python ~/.claude/skills/vpn-check/scripts/check_vpn.py --quiet
```

### Step 2: Load Credentials
```bash
cat ~/.claude/skills/s3-access/references/.credentials
```
If missing, invoke `/credential-setup s3-access`.

### Step 3: Execute S3 Operation
```bash
~/.claude/skills/s3-access/scripts/s3_access.py buckets
~/.claude/skills/s3-access/scripts/s3_access.py ls my-bucket
~/.claude/skills/s3-access/scripts/s3_access.py get my-bucket/path/to/file.txt
```

### Step 4: Return Results
- **List**: Return bucket/object listing
- **Get**: Return file contents or download confirmation
- **Put**: Return upload confirmation with object URL
- **Errors**: Show error with suggestions

---

## Script Usage

```bash
# List all buckets
~/.claude/skills/s3-access/scripts/s3_access.py buckets

# List objects in a bucket (with optional prefix)
~/.claude/skills/s3-access/scripts/s3_access.py ls my-bucket
~/.claude/skills/s3-access/scripts/s3_access.py ls my-bucket/path/to/folder/

# Get object contents (display or download)
~/.claude/skills/s3-access/scripts/s3_access.py get my-bucket/path/to/file.txt
~/.claude/skills/s3-access/scripts/s3_access.py get my-bucket/path/to/file.txt --output local-file.txt

# Upload a file
~/.claude/skills/s3-access/scripts/s3_access.py put local-file.txt my-bucket/path/to/destination.txt

# Get object info/metadata
~/.claude/skills/s3-access/scripts/s3_access.py info my-bucket/path/to/file.txt

# Delete an object
~/.claude/skills/s3-access/scripts/s3_access.py rm my-bucket/path/to/file.txt

# Copy objects between locations
~/.claude/skills/s3-access/scripts/s3_access.py cp my-bucket/source.txt my-bucket/dest.txt

# Use specific AWS profile
~/.claude/skills/s3-access/scripts/s3_access.py buckets --profile production

# Use specific region
~/.claude/skills/s3-access/scripts/s3_access.py ls my-bucket --region eu-west-1
```

### Arguments

| Argument | Description |
|----------|-------------|
| `buckets` | List all accessible S3 buckets |
| `ls <bucket>[/prefix]` | List objects in bucket with optional prefix |
| `get <bucket/key>` | Get object contents or download |
| `put <local> <bucket/key>` | Upload local file to S3 |
| `info <bucket/key>` | Get object metadata |
| `rm <bucket/key>` | Delete an object |
| `cp <src> <dest>` | Copy object between locations |
| `--profile`, `-p` | AWS profile name (default: from credentials) |
| `--region`, `-r` | AWS region (default: from credentials or us-east-1) |
| `--output`, `-o` | Write get output to file |
| `--recursive` | For ls: list all objects recursively |
| `--limit`, `-l` | Limit number of results |

---

## Examples

### List Buckets
```
User: Show me all S3 buckets

Claude:
1. Execute: s3_access.py buckets
2. Return list of buckets with creation dates
```

### Browse Bucket Contents
```
User: What files are in the data-exports bucket?

Claude:
1. Execute: s3_access.py ls data-exports
2. Return listing with sizes and last modified dates
```

### Download a File
```
User: Download the config file from s3://my-app/config/settings.json

Claude:
1. Execute: s3_access.py get my-app/config/settings.json --output settings.json
2. Confirm download location and file size
```

### Upload a File
```
User: Upload report.pdf to s3://reports/2026/january/

Claude:
1. Execute: s3_access.py put report.pdf reports/2026/january/report.pdf
2. Return S3 URI and confirm upload
```

### Get File Metadata
```
User: What's the size of that log file?

Claude:
1. Execute: s3_access.py info logs-bucket/app/2026-01-09.log
2. Return size, content type, last modified, ETag
```

---

## Edge Cases

| Case | Handling |
|------|----------|
| Bucket not found | Show error, suggest checking bucket name |
| Access denied | Check IAM permissions, suggest policy review |
| Object not found | Show error, suggest checking key path |
| Region mismatch | Auto-redirect or suggest correct region |
| Large file download | Show progress, warn about size |
| Missing credentials | Prompt to run `/credential-setup` |
| VPN not connected | Suggest connecting to VPN (for VPC endpoints) |

---

## Configuration

### Credential Structure
```
AWS_ACCESS_KEY_ID     - AWS access key (required unless using profile)
AWS_SECRET_ACCESS_KEY - AWS secret key (required unless using profile)
AWS_DEFAULT_REGION    - Default AWS region (optional, defaults to us-east-1)
AWS_PROFILE           - Named profile to use (optional)
AWS_ENDPOINT_URL      - Custom endpoint URL (optional, for VPC endpoints or S3-compatible)
```

### First-Time Setup
```bash
cd s3-access/references
cp .credentials.example .credentials
# Edit .credentials with your values
chmod 600 .credentials  # Secure permissions
```

### Getting AWS Credentials

**From AWS Console:**
1. Go to IAM > Users > Your User > Security credentials
2. Create access key
3. Copy Access Key ID and Secret Access Key

**From AWS CLI:**
```bash
aws configure
# Creates ~/.aws/credentials automatically
```

**Using Profiles:**
```bash
# In ~/.aws/credentials
[default]
aws_access_key_id = AKIA...
aws_secret_access_key = ...

[production]
aws_access_key_id = AKIA...
aws_secret_access_key = ...
```

---

## Security

- **Least privilege**: Use IAM policies with minimum required permissions
- **Never commit credentials**: `.credentials` is in `.gitignore`
- **Use profiles**: Prefer named profiles over hardcoded keys
- **Rotate keys**: Regularly rotate access keys
- **VPC endpoints**: Consider VPC endpoints for private access
- **File permissions**: `.credentials` should be 600 (owner read/write only)

---

## Required IAM Permissions

Minimum permissions for full functionality:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:ListAllMyBuckets",
                "s3:ListBucket",
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject",
                "s3:GetObjectAttributes",
                "s3:HeadObject",
                "s3:CopyObject"
            ],
            "Resource": [
                "arn:aws:s3:::*",
                "arn:aws:s3:::*/*"
            ]
        }
    ]
}
```

For read-only access, remove `PutObject`, `DeleteObject`, and `CopyObject`.
