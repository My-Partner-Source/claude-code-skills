---
name: sftp-access
description: "Access remote SFTP servers for file operations. List directories, upload/download files, get file metadata, and manage remote files. Supports password and SSH key authentication. Use when user needs to interact with SFTP/SSH servers."
version: 1.0.0
---

# SFTP Access

Access remote SFTP servers for file transfer and management operations.

## Key Behavior

**Authentication**: Supports both password and SSH private key authentication.

**Operations**: List directories, upload/download files, get metadata, delete files, create directories.

**Connection**: Uses paramiko library for SSH/SFTP connections with configurable timeout.

## Prerequisites

### Stacked Skills
- **vpn-check** — Run `/vpn-check` before accessing internal SFTP servers (if required)
- **credential-setup** — Run `/credential-setup sftp-access` if `.credentials` missing

### Dependencies

**One-time setup** (creates virtual environment and installs paramiko):

```bash
cd ~/.claude/skills/sftp-access && bash setup.sh
```

This creates a `.venv` folder and configures the script to use it automatically.

---

## Workflow

### Step 1: Verify VPN (if accessing internal servers)
```bash
python ~/.claude/skills/vpn-check/scripts/check_vpn.py --quiet
```

### Step 2: Load Credentials
```bash
cat ~/.claude/skills/sftp-access/references/.credentials
```
If missing, invoke `/credential-setup sftp-access`.

### Step 3: Execute SFTP Operation
```bash
~/.claude/skills/sftp-access/scripts/sftp_access.py ls /remote/path
~/.claude/skills/sftp-access/scripts/sftp_access.py get /remote/file.txt
~/.claude/skills/sftp-access/scripts/sftp_access.py put local.txt /remote/file.txt
```

### Step 4: Return Results
- **List**: Return directory listing with file sizes and dates
- **Get**: Return file contents or download confirmation
- **Put**: Return upload confirmation
- **Errors**: Show error with suggestions

---

## Script Usage

```bash
# List remote directory
~/.claude/skills/sftp-access/scripts/sftp_access.py ls /path/to/directory
~/.claude/skills/sftp-access/scripts/sftp_access.py ls /home/user/data/

# Get file contents (display or download)
~/.claude/skills/sftp-access/scripts/sftp_access.py get /path/to/file.txt
~/.claude/skills/sftp-access/scripts/sftp_access.py get /path/to/file.txt --output local-file.txt

# Upload a file
~/.claude/skills/sftp-access/scripts/sftp_access.py put local-file.txt /remote/path/to/destination.txt

# Get file info/metadata
~/.claude/skills/sftp-access/scripts/sftp_access.py info /path/to/file.txt

# Delete a remote file
~/.claude/skills/sftp-access/scripts/sftp_access.py rm /path/to/file.txt

# Create remote directory
~/.claude/skills/sftp-access/scripts/sftp_access.py mkdir /path/to/new/directory

# Delete remote directory (must be empty)
~/.claude/skills/sftp-access/scripts/sftp_access.py rmdir /path/to/directory

# Use specific host/port/user
~/.claude/skills/sftp-access/scripts/sftp_access.py ls /path --host sftp.example.com --user myuser

# Use SSH key authentication
~/.claude/skills/sftp-access/scripts/sftp_access.py ls /path --key ~/.ssh/id_rsa
```

### Arguments

| Argument | Description |
|----------|-------------|
| `ls <path>` | List remote directory contents |
| `get <remote-path>` | Get file contents or download |
| `put <local> <remote>` | Upload local file to SFTP server |
| `info <path>` | Get file/directory metadata |
| `rm <path>` | Delete a remote file |
| `mkdir <path>` | Create remote directory |
| `rmdir <path>` | Remove remote directory (must be empty) |
| `--host`, `-H` | SFTP server hostname |
| `--port`, `-P` | SFTP server port (default: 22) |
| `--user`, `-u` | Username for authentication |
| `--password`, `-p` | Password (use credentials file instead) |
| `--key`, `-k` | Path to SSH private key file |
| `--output`, `-o` | Write get output to local file |
| `--yes`, `-y` | Skip delete confirmation |
| `--timeout`, `-t` | Connection timeout in seconds (default: 30) |

---

## Examples

### List Directory
```
User: Show me files in /var/log on sftp.example.com

Claude:
1. Execute: sftp_access.py ls /var/log --host sftp.example.com
2. Return listing with sizes and last modified dates
```

### Download a File
```
User: Download the config file from /etc/app/config.yaml

Claude:
1. Execute: sftp_access.py get /etc/app/config.yaml --output config.yaml
2. Confirm download location and file size
```

### Upload a File
```
User: Upload report.pdf to /uploads/2026/january/

Claude:
1. Execute: sftp_access.py put report.pdf /uploads/2026/january/report.pdf
2. Confirm upload with file size
```

### Get File Metadata
```
User: What's the size of that log file?

Claude:
1. Execute: sftp_access.py info /var/log/app.log
2. Return size, permissions, owner, last modified
```

---

## Edge Cases

| Case | Handling |
|------|----------|
| Connection refused | Check hostname, port, and network connectivity |
| Authentication failed | Verify username/password or SSH key |
| Permission denied | Check file permissions on remote server |
| File not found | Show error, suggest checking path |
| Directory not empty | Cannot rmdir non-empty directories |
| Timeout | Increase timeout or check network |
| Missing credentials | Prompt to run `/credential-setup` |
| VPN not connected | Suggest connecting to VPN |

---

## Configuration

### Credential Structure
```
SFTP_HOST          - SFTP server hostname (required)
SFTP_PORT          - SFTP server port (optional, default: 22)
SFTP_USERNAME      - Username for authentication (required)
SFTP_PASSWORD      - Password (optional if using key)
SFTP_KEY_FILE      - Path to SSH private key (optional if using password)
SFTP_KEY_PASSPHRASE - Passphrase for encrypted private key (optional)
```

### First-Time Setup
```bash
cd sftp-access/references
cp .credentials.example .credentials
# Edit .credentials with your values
chmod 600 .credentials  # Secure permissions
```

### SSH Key Authentication
```bash
# Generate SSH key pair (if needed)
ssh-keygen -t ed25519 -C "your-email@example.com"

# Add public key to remote server
ssh-copy-id user@sftp.example.com

# Set key path in .credentials
SFTP_KEY_FILE="/home/user/.ssh/id_ed25519"
```

---

## Security

- **Use SSH keys**: Prefer key-based authentication over passwords
- **Protect private keys**: Set permissions to 600 (owner read/write only)
- **Never commit credentials**: `.credentials` is in `.gitignore`
- **Use passphrase**: Protect private keys with a passphrase
- **Rotate credentials**: Change passwords/keys regularly
- **Limit access**: Use the principle of least privilege on servers
- **File permissions**: `.credentials` should be 600 (owner read/write only)

---

## Troubleshooting

### Connection Issues
```bash
# Test basic SSH connectivity
ssh -v user@host -p 22

# Check if SFTP subsystem is enabled on server
# In /etc/ssh/sshd_config: Subsystem sftp /usr/lib/openssh/sftp-server
```

### Key Authentication Issues
```bash
# Verify key permissions
ls -la ~/.ssh/id_*
# Should be: -rw------- (600) for private key

# Test key manually
ssh -i ~/.ssh/id_rsa user@host
```

### Permission Errors
- Check file/directory permissions on remote server
- Verify user has appropriate access rights
- Check if SELinux or AppArmor is blocking access
