---
name: aws-sso-env-switcher
description: "Switch between AWS environments (DEV/QA/UAT/PROD) using AWS SSO and manage kubectl contexts for EKS clusters. Authenticate via SSO, switch environments, and run kubectl commands against the correct cluster."
version: 1.0.0
---

# AWS SSO Environment Switcher

Switch between AWS environments using AWS SSO and manage kubectl contexts for EKS clusters.

## Key Behavior

**Environment Confirmation Required**: If environment is ambiguous or not specified, ASK the user:
- "Which environment should I switch to? DEV / QA / UAT / PROD"

**SSO Authentication**: Uses AWS SSO for secure authentication without static credentials.

**kubectl Integration**: Automatically configures kubectl context for the selected environment's EKS cluster.

## Prerequisites

### Stacked Skills
- **vpn-check** — Run `/vpn-check` if clusters are behind VPN
- **credential-setup** — Run `/credential-setup aws-sso-env-switcher` if `.credentials` missing

### Dependencies

**One-time setup** (creates virtual environment and installs boto3):

```bash
cd ~/.claude/skills/aws-sso-env-switcher && bash setup.sh
```

This creates a `.venv` folder and configures the script to use it automatically.

### System Requirements

- **AWS CLI v2** — Required for SSO login (`aws --version` should be 2.x)
- **kubectl** — Kubernetes CLI for cluster operations

---

## Workflow

### Step 1: Verify VPN (if required)
```bash
python ~/.claude/skills/vpn-check/scripts/check_vpn.py --quiet
```

### Step 2: Load Configuration
```bash
cat ~/.claude/skills/aws-sso-env-switcher/references/.credentials
```
If missing, invoke `/credential-setup aws-sso-env-switcher`.

### Step 3: Determine Environment
From user request, detect target:
- **Explicit**: "switch to DEV", "use PROD", "connect to QA"
- **Ambiguous**: No env mentioned → **ASK user**

### Step 4: Authenticate and Switch
```bash
~/.claude/skills/aws-sso-env-switcher/scripts/aws_sso_env.py switch --env <ENV>
```

### Step 5: Run kubectl Commands
```bash
~/.claude/skills/aws-sso-env-switcher/scripts/aws_sso_env.py kubectl -- get pods
~/.claude/skills/aws-sso-env-switcher/scripts/aws_sso_env.py kubectl -- get deployments
```

---

## Script Usage

```bash
# Check SSO login status
~/.claude/skills/aws-sso-env-switcher/scripts/aws_sso_env.py status

# Switch to an environment (authenticates via SSO if needed)
~/.claude/skills/aws-sso-env-switcher/scripts/aws_sso_env.py switch --env DEV
~/.claude/skills/aws-sso-env-switcher/scripts/aws_sso_env.py switch --env QA
~/.claude/skills/aws-sso-env-switcher/scripts/aws_sso_env.py switch --env UAT
~/.claude/skills/aws-sso-env-switcher/scripts/aws_sso_env.py switch --env PROD

# Run kubectl commands in current environment
~/.claude/skills/aws-sso-env-switcher/scripts/aws_sso_env.py kubectl -- get pods
~/.claude/skills/aws-sso-env-switcher/scripts/aws_sso_env.py kubectl -- get pods -n my-namespace
~/.claude/skills/aws-sso-env-switcher/scripts/aws_sso_env.py kubectl -- logs deployment/my-app

# Run kubectl in a specific environment (switch + command)
~/.claude/skills/aws-sso-env-switcher/scripts/aws_sso_env.py kubectl --env PROD -- get pods
~/.claude/skills/aws-sso-env-switcher/scripts/aws_sso_env.py kubectl --env DEV -- describe pod my-pod

# List available environments
~/.claude/skills/aws-sso-env-switcher/scripts/aws_sso_env.py list

# Show current environment and context
~/.claude/skills/aws-sso-env-switcher/scripts/aws_sso_env.py current

# Force SSO login (refresh tokens)
~/.claude/skills/aws-sso-env-switcher/scripts/aws_sso_env.py login --env DEV

# Update kubeconfig for an environment
~/.claude/skills/aws-sso-env-switcher/scripts/aws_sso_env.py update-kubeconfig --env QA
```

### Arguments

| Argument | Description |
|----------|-------------|
| `status` | Check SSO authentication status |
| `switch --env <ENV>` | Switch to environment (DEV/QA/UAT/PROD) |
| `kubectl --env <ENV> -- <args>` | Run kubectl command in environment |
| `list` | List configured environments |
| `current` | Show current environment and kubectl context |
| `login --env <ENV>` | Force SSO login for environment |
| `update-kubeconfig --env <ENV>` | Update kubectl config for EKS cluster |

---

## Examples

### Switch Environment
```
User: Switch to the DEV environment

Claude:
1. Check SSO status for DEV profile
2. Execute: aws_sso_env.py switch --env DEV
3. Report: "Switched to DEV environment (cluster: my-app-dev-eks)"
```

### Run kubectl Command
```
User: Get all pods in PROD

Claude:
1. Verify current env or switch to PROD
2. Execute: aws_sso_env.py kubectl --env PROD -- get pods
3. Return pod listing in table format
```

### Check Deployment Status
```
User: Show me the my-service deployment in QA

Claude:
1. Execute: aws_sso_env.py kubectl --env QA -- get deployment my-service -o wide
2. Return deployment details
```

### View Pod Logs
```
User: Get logs from the api pod in UAT

Claude:
1. Execute: aws_sso_env.py kubectl --env UAT -- logs deployment/api --tail=100
2. Return log output
```

### Scale Deployment
```
User: Scale my-app to 3 replicas in DEV

Claude:
1. Confirm: "This will scale my-app to 3 replicas in DEV. Proceed? [y/N]"
2. Execute: aws_sso_env.py kubectl --env DEV -- scale deployment/my-app --replicas=3
3. Report: "Deployment my-app scaled to 3 replicas"
```

---

## Edge Cases

| Case | Handling |
|------|----------|
| No environment specified | Ask: "DEV / QA / UAT / PROD?" |
| SSO session expired | Automatically trigger `aws sso login` |
| Missing kubeconfig | Run `aws eks update-kubeconfig` |
| Cluster unreachable | Check VPN, verify cluster endpoint |
| kubectl not installed | Show error with installation instructions |
| AWS CLI v1 | Show error, suggest upgrading to v2 |
| Invalid profile | List available profiles from config |

---

## Safety Features

| Feature | Behavior |
|---------|----------|
| **Environment Display** | Always shows current environment before operations |
| **PROD Warning** | Extra confirmation for PROD destructive operations |
| **Dry Run Support** | Use `kubectl --dry-run=client` for previews |
| **Context Isolation** | Each environment uses distinct kubectl context |

### Destructive Operations

These kubectl operations require confirmation in PROD:
- `delete` — Deletes resources
- `scale --replicas=0` — Scales to zero
- `rollout restart` — Restarts deployments
- `apply` — Applies changes
- `patch` — Patches resources

---

## Configuration

### Credential Structure
```
# AWS SSO Configuration
AWS_SSO_START_URL     - SSO portal URL (e.g., https://mycompany.awsapps.com/start)
AWS_SSO_REGION        - SSO region (e.g., us-east-1)

# Per-Environment Configuration
AWS_{ENV}_SSO_ACCOUNT_ID   - AWS account ID for environment
AWS_{ENV}_SSO_ROLE_NAME    - SSO role name to assume
AWS_{ENV}_EKS_CLUSTER      - EKS cluster name
AWS_{ENV}_EKS_REGION       - EKS cluster region (optional, defaults to SSO region)
AWS_{ENV}_NAMESPACE        - Default namespace (optional)
```

### First-Time Setup
```bash
cd ~/.claude/skills/aws-sso-env-switcher/references
cp .credentials.example .credentials
# Edit .credentials with your SSO and cluster details
chmod 600 .credentials  # Secure permissions
```

### AWS CLI SSO Profile Setup

The skill can create AWS CLI profiles automatically, or you can configure them manually:

```bash
# In ~/.aws/config
[profile dev-sso]
sso_start_url = https://mycompany.awsapps.com/start
sso_region = us-east-1
sso_account_id = 123456789012
sso_role_name = DeveloperAccess
region = us-east-1

[profile prod-sso]
sso_start_url = https://mycompany.awsapps.com/start
sso_region = us-east-1
sso_account_id = 987654321098
sso_role_name = DeveloperAccess
region = us-east-1
```

---

## Security

- **No static credentials** — Uses SSO for all authentication
- **Session-based** — SSO tokens expire (typically 1-8 hours)
- **Role-based access** — Uses SSO roles with defined permissions
- **Audit trail** — All SSO logins logged in AWS CloudTrail
- **Context separation** — Each environment uses distinct kubectl context
- **File permissions** — `.credentials` should be 600 (owner read/write only)

---

## Troubleshooting

### SSO Login Issues

**"Token has expired"**
```bash
~/.claude/skills/aws-sso-env-switcher/scripts/aws_sso_env.py login --env DEV
```

**"No browser available"**
Set `AWS_SSO_LOGIN_METHOD=sso-session` and use `--no-browser` mode.

### kubectl Issues

**"Unable to connect to the server"**
1. Check VPN connection: `/vpn-check`
2. Verify cluster endpoint is reachable
3. Update kubeconfig: `aws_sso_env.py update-kubeconfig --env <ENV>`

**"Unauthorized"**
1. Refresh SSO session: `aws_sso_env.py login --env <ENV>`
2. Verify role has EKS access permissions

### Profile Issues

**"Profile not found"**
1. Check `.credentials` file exists
2. Verify profile names match configuration
3. Run `aws_sso_env.py list` to see configured environments

---

## Required IAM Permissions

Minimum permissions for kubectl operations:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "eks:DescribeCluster",
                "eks:ListClusters"
            ],
            "Resource": "*"
        }
    ]
}
```

Kubernetes RBAC must also be configured to allow the SSO role to access cluster resources.
