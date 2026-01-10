#!/usr/bin/env python3
"""AWS SSO Environment Switcher with kubectl integration.

Switch between AWS environments (DEV/QA/UAT/PROD) using AWS SSO and manage
kubectl contexts for EKS clusters.

Usage:
    aws_sso_env.py status
    aws_sso_env.py switch --env DEV
    aws_sso_env.py kubectl --env PROD -- get pods
    aws_sso_env.py list
    aws_sso_env.py current
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

# Venv auto-detection and re-exec
_SKILL_DIR = Path(__file__).parent.parent
_VENV_DIR = _SKILL_DIR / ".venv"
_VENV_PYTHON = _VENV_DIR / "bin" / "python3"
_SETUP_SCRIPT = _SKILL_DIR / "setup.sh"

if not sys.prefix.startswith(str(_VENV_DIR)):
    if _VENV_PYTHON.exists():
        os.execv(str(_VENV_PYTHON), [str(_VENV_PYTHON)] + sys.argv)
    else:
        print("Error: Virtual environment not found.")
        print(f"Run setup first: cd {_SKILL_DIR} && bash setup.sh")
        sys.exit(1)

# Constants
SKILL_DIR = Path(__file__).parent.parent
CREDENTIALS_FILE = SKILL_DIR / "references" / ".credentials"
VALID_ENVS = ["DEV", "QA", "UAT", "PROD"]

# Credential file search paths (in priority order)
CREDENTIAL_PATHS = [
    CREDENTIALS_FILE,
    Path.home() / ".claude" / "skills" / "aws-sso-env-switcher" / ".credentials",
    Path(".credentials"),
]

# Destructive kubectl operations that require PROD confirmation
DESTRUCTIVE_OPERATIONS = [
    "delete",
    "scale",
    "rollout",
    "apply",
    "patch",
    "replace",
    "drain",
    "cordon",
    "taint",
]


class Config:
    """Configuration container for AWS SSO and EKS settings."""

    def __init__(self):
        self.sso_start_url = ""
        self.sso_region = ""
        self.environments = {}  # ENV -> {account_id, role_name, cluster, region, namespace}

    @classmethod
    def load(cls) -> "Config":
        """Load configuration from .credentials file and environment variables."""
        config = cls()

        # Find credentials file
        creds_file = None
        for path in CREDENTIAL_PATHS:
            if path.exists():
                creds_file = path
                break

        # Parse credentials file
        creds = {}
        if creds_file:
            with open(creds_file) as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue

                    # Parse: export VAR="value" or VAR="value"
                    line = line.replace("export ", "")
                    match = re.match(r'(\w+)=["\']?([^"\']*)["\']?', line)
                    if match:
                        creds[match.group(1)] = match.group(2)

        # Override with environment variables
        for key in list(creds.keys()):
            env_val = os.environ.get(key)
            if env_val:
                creds[key] = env_val

        # Load SSO configuration
        config.sso_start_url = creds.get("AWS_SSO_START_URL", "")
        config.sso_region = creds.get("AWS_SSO_REGION", "us-east-1")

        # Load per-environment configuration
        for env in VALID_ENVS:
            account_id = creds.get(f"AWS_{env}_SSO_ACCOUNT_ID", "")
            role_name = creds.get(f"AWS_{env}_SSO_ROLE_NAME", "")
            cluster = creds.get(f"AWS_{env}_EKS_CLUSTER", "")
            region = creds.get(f"AWS_{env}_EKS_REGION", config.sso_region)
            namespace = creds.get(f"AWS_{env}_NAMESPACE", "default")

            if account_id and role_name:
                config.environments[env] = {
                    "account_id": account_id,
                    "role_name": role_name,
                    "cluster": cluster,
                    "region": region,
                    "namespace": namespace,
                    "profile": f"{env.lower()}-sso",
                }

        return config

    def get_env(self, env: str) -> dict:
        """Get configuration for a specific environment."""
        env = env.upper()
        if env not in self.environments:
            available = ", ".join(self.environments.keys()) or "None configured"
            print(f"Error: Environment '{env}' not configured")
            print(f"Available environments: {available}")
            sys.exit(1)
        return self.environments[env]


def check_dependencies():
    """Verify required tools are installed."""
    # Check AWS CLI
    if not shutil.which("aws"):
        print("Error: AWS CLI not found")
        print("Install from: https://aws.amazon.com/cli/")
        sys.exit(1)

    # Check AWS CLI version (need v2 for SSO)
    try:
        result = subprocess.run(
            ["aws", "--version"],
            capture_output=True,
            text=True,
        )
        version_match = re.search(r"aws-cli/(\d+)\.", result.stdout)
        if version_match and int(version_match.group(1)) < 2:
            print("Error: AWS CLI v2 required for SSO support")
            print(f"Current version: {result.stdout.strip()}")
            print("Upgrade from: https://aws.amazon.com/cli/")
            sys.exit(1)
    except Exception:
        pass  # Proceed if version check fails

    # Check kubectl
    if not shutil.which("kubectl"):
        print("Error: kubectl not found")
        print("Install from: https://kubernetes.io/docs/tasks/tools/")
        sys.exit(1)


def get_profile_name(env: str) -> str:
    """Get AWS profile name for environment."""
    return f"{env.lower()}-sso"


def ensure_aws_profile(config: Config, env: str):
    """Ensure AWS CLI profile exists for the environment."""
    env_config = config.get_env(env)
    profile = env_config["profile"]

    # Check if profile exists in ~/.aws/config
    aws_config_path = Path.home() / ".aws" / "config"

    profile_exists = False
    if aws_config_path.exists():
        with open(aws_config_path) as f:
            content = f.read()
            if f"[profile {profile}]" in content:
                profile_exists = True

    if not profile_exists:
        print(f"Creating AWS profile: {profile}")

        # Create profile configuration
        profile_config = f"""
[profile {profile}]
sso_start_url = {config.sso_start_url}
sso_region = {config.sso_region}
sso_account_id = {env_config['account_id']}
sso_role_name = {env_config['role_name']}
region = {env_config['region']}
"""

        # Ensure directory exists
        aws_config_path.parent.mkdir(parents=True, exist_ok=True)

        # Append to config file
        with open(aws_config_path, "a") as f:
            f.write(profile_config)

        print(f"Profile '{profile}' created in {aws_config_path}")


def check_sso_session(profile: str) -> bool:
    """Check if SSO session is valid for the profile."""
    try:
        result = subprocess.run(
            ["aws", "sts", "get-caller-identity", "--profile", profile],
            capture_output=True,
            text=True,
            timeout=10,
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        return False
    except Exception:
        return False


def sso_login(profile: str):
    """Perform SSO login for the profile."""
    print(f"Initiating SSO login for profile: {profile}")
    print("A browser window will open for authentication...")
    print()

    try:
        result = subprocess.run(
            ["aws", "sso", "login", "--profile", profile],
            check=False,
        )
        if result.returncode != 0:
            print("Error: SSO login failed")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\nSSO login cancelled")
        sys.exit(1)


def update_kubeconfig(config: Config, env: str):
    """Update kubeconfig for the EKS cluster."""
    env_config = config.get_env(env)
    profile = env_config["profile"]
    cluster = env_config["cluster"]
    region = env_config["region"]

    if not cluster:
        print(f"Warning: No EKS cluster configured for {env}")
        return

    print(f"Updating kubeconfig for cluster: {cluster}")

    try:
        result = subprocess.run(
            [
                "aws", "eks", "update-kubeconfig",
                "--name", cluster,
                "--region", region,
                "--profile", profile,
                "--alias", f"{env.lower()}-{cluster}",
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            print(f"Error updating kubeconfig: {result.stderr}")
            sys.exit(1)

        print(f"Kubeconfig updated for {env} ({cluster})")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def set_kubectl_context(config: Config, env: str):
    """Set kubectl context to the environment's cluster."""
    env_config = config.get_env(env)
    cluster = env_config["cluster"]

    if not cluster:
        return

    context_name = f"{env.lower()}-{cluster}"

    # Check if context exists
    result = subprocess.run(
        ["kubectl", "config", "get-contexts", "-o", "name"],
        capture_output=True,
        text=True,
    )

    if context_name not in result.stdout.split("\n"):
        # Context doesn't exist, update kubeconfig
        update_kubeconfig(config, env)

    # Set current context
    subprocess.run(
        ["kubectl", "config", "use-context", context_name],
        capture_output=True,
    )


def get_current_context() -> str:
    """Get current kubectl context."""
    result = subprocess.run(
        ["kubectl", "config", "current-context"],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        return result.stdout.strip()
    return "none"


def is_destructive_operation(kubectl_args: list) -> bool:
    """Check if kubectl command is a destructive operation."""
    if not kubectl_args:
        return False

    cmd = kubectl_args[0].lower()
    return cmd in DESTRUCTIVE_OPERATIONS


def confirm_prod_operation(kubectl_args: list) -> bool:
    """Require explicit confirmation for PROD destructive operations."""
    print()
    print("=" * 60)
    print("  PRODUCTION ENVIRONMENT - DESTRUCTIVE OPERATION")
    print("=" * 60)
    print()
    print(f"  Command: kubectl {' '.join(kubectl_args)}")
    print()
    print("  This will modify the PRODUCTION cluster.")
    print()
    response = input("  Type 'PROD' to confirm, or anything else to cancel: ")
    print()

    return response.strip() == "PROD"


def run_kubectl(config: Config, env: str, kubectl_args: list):
    """Run kubectl command in the specified environment."""
    env_config = config.get_env(env)
    profile = env_config["profile"]
    cluster = env_config["cluster"]
    namespace = env_config["namespace"]

    # Ensure SSO session is valid
    if not check_sso_session(profile):
        print(f"SSO session expired for {env}, logging in...")
        sso_login(profile)

    # Ensure kubeconfig is set up
    set_kubectl_context(config, env)

    # Check for destructive operations in PROD
    if env.upper() == "PROD" and is_destructive_operation(kubectl_args):
        if not confirm_prod_operation(kubectl_args):
            print("Operation cancelled")
            return

    # Build kubectl command
    context_name = f"{env.lower()}-{cluster}"
    cmd = ["kubectl", "--context", context_name]

    # Add namespace if not specified in args
    if "-n" not in kubectl_args and "--namespace" not in kubectl_args:
        if namespace and namespace != "default":
            cmd.extend(["-n", namespace])

    cmd.extend(kubectl_args)

    # Show environment banner
    print(f"[{env}] Running: kubectl {' '.join(kubectl_args)}")
    print("-" * 60)

    # Execute kubectl
    try:
        result = subprocess.run(cmd)
        sys.exit(result.returncode)
    except KeyboardInterrupt:
        print("\nCommand cancelled")
        sys.exit(130)


def cmd_status(config: Config, args):
    """Show SSO authentication status for all environments."""
    print("\nAWS SSO Status")
    print("=" * 60)
    print(f"SSO Start URL: {config.sso_start_url}")
    print(f"SSO Region:    {config.sso_region}")
    print()

    if not config.environments:
        print("No environments configured.")
        print("Set up .credentials file with environment configurations.")
        return

    print("Environment Status:")
    print("-" * 60)

    for env, env_config in config.environments.items():
        profile = env_config["profile"]
        cluster = env_config["cluster"] or "Not configured"

        # Check session status
        if check_sso_session(profile):
            status = "Authenticated"
            status_icon = "[OK]"
        else:
            status = "Not authenticated"
            status_icon = "[--]"

        print(f"  {status_icon} {env:<6} | Profile: {profile:<12} | Cluster: {cluster}")

    print()


def cmd_switch(config: Config, args):
    """Switch to an environment."""
    env = args.env.upper()

    if env not in VALID_ENVS:
        print(f"Error: Invalid environment '{env}'")
        print(f"Valid environments: {', '.join(VALID_ENVS)}")
        sys.exit(1)

    env_config = config.get_env(env)
    profile = env_config["profile"]
    cluster = env_config["cluster"]

    print(f"\nSwitching to {env} environment...")
    print("-" * 40)

    # Ensure profile exists
    ensure_aws_profile(config, env)

    # Check/refresh SSO session
    if not check_sso_session(profile):
        print("SSO session not active, initiating login...")
        sso_login(profile)

    # Update kubeconfig if cluster is configured
    if cluster:
        update_kubeconfig(config, env)
        set_kubectl_context(config, env)

        # Verify connection
        context_name = f"{env.lower()}-{cluster}"
        print(f"\nVerifying cluster connection...")
        result = subprocess.run(
            ["kubectl", "--context", context_name, "cluster-info"],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            print(f"\nSuccessfully connected to {env} environment")
            print(f"  Cluster: {cluster}")
            print(f"  Context: {context_name}")
        else:
            print(f"\nWarning: Could not verify cluster connection")
            print(f"  {result.stderr.strip()}")
            print("\nTry checking VPN or cluster status.")
    else:
        print(f"\nSwitched to {env} (no EKS cluster configured)")

    print()


def cmd_kubectl(config: Config, args):
    """Run kubectl command in an environment."""
    env = args.env.upper() if args.env else None

    # If no env specified, try to detect from current context
    if not env:
        current = get_current_context()
        for e in config.environments:
            cluster = config.environments[e].get("cluster", "")
            if cluster and e.lower() in current.lower():
                env = e
                break

        if not env:
            print("Error: No environment specified and could not detect from context")
            print("Use: aws_sso_env.py kubectl --env <ENV> -- <kubectl-args>")
            sys.exit(1)

    run_kubectl(config, env, args.kubectl_args)


def cmd_list(config: Config, args):
    """List available environments."""
    print("\nConfigured Environments")
    print("=" * 70)

    if not config.environments:
        print("No environments configured.")
        print()
        print("Add environment configurations to .credentials:")
        print("  AWS_DEV_SSO_ACCOUNT_ID, AWS_DEV_SSO_ROLE_NAME, AWS_DEV_EKS_CLUSTER")
        print()
        return

    print(f"{'Env':<6} {'Account ID':<14} {'Role':<20} {'Cluster':<20} {'Region':<12}")
    print("-" * 70)

    for env, cfg in config.environments.items():
        print(f"{env:<6} {cfg['account_id']:<14} {cfg['role_name']:<20} "
              f"{cfg['cluster'] or 'N/A':<20} {cfg['region']:<12}")

    print()


def cmd_current(config: Config, args):
    """Show current environment and kubectl context."""
    print("\nCurrent Environment")
    print("=" * 50)

    # Get current kubectl context
    current_context = get_current_context()
    print(f"kubectl context: {current_context}")

    # Try to detect environment from context
    detected_env = None
    for env, cfg in config.environments.items():
        cluster = cfg.get("cluster", "")
        if cluster and env.lower() in current_context.lower():
            detected_env = env
            break

    if detected_env:
        cfg = config.environments[detected_env]
        print(f"Environment:     {detected_env}")
        print(f"Cluster:         {cfg['cluster']}")
        print(f"Region:          {cfg['region']}")
        print(f"Namespace:       {cfg['namespace']}")
    else:
        print("Environment:     Unknown (context not matching configured environments)")

    print()


def cmd_login(config: Config, args):
    """Force SSO login for an environment."""
    env = args.env.upper()
    env_config = config.get_env(env)
    profile = env_config["profile"]

    # Ensure profile exists
    ensure_aws_profile(config, env)

    # Force login
    sso_login(profile)

    print(f"\nSSO login successful for {env}")


def cmd_update_kubeconfig(config: Config, args):
    """Update kubeconfig for an environment's EKS cluster."""
    env = args.env.upper()
    env_config = config.get_env(env)
    profile = env_config["profile"]

    # Ensure SSO session
    if not check_sso_session(profile):
        print("SSO session not active, initiating login...")
        sso_login(profile)

    update_kubeconfig(config, env)


def main():
    check_dependencies()

    parser = argparse.ArgumentParser(
        description="AWS SSO Environment Switcher with kubectl integration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s status                          Check SSO status
  %(prog)s switch --env DEV                Switch to DEV environment
  %(prog)s kubectl --env PROD -- get pods  Get pods in PROD
  %(prog)s kubectl -- get deployments      Use current context
  %(prog)s list                            List environments
  %(prog)s current                         Show current environment
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # status command
    subparsers.add_parser("status", help="Check SSO authentication status")

    # switch command
    switch_parser = subparsers.add_parser("switch", help="Switch to an environment")
    switch_parser.add_argument("--env", "-e", required=True,
                               choices=VALID_ENVS, help="Target environment")

    # kubectl command
    kubectl_parser = subparsers.add_parser("kubectl", help="Run kubectl command")
    kubectl_parser.add_argument("--env", "-e", choices=VALID_ENVS,
                                help="Target environment (optional)")
    kubectl_parser.add_argument("kubectl_args", nargs="*", help="kubectl arguments")

    # list command
    subparsers.add_parser("list", help="List configured environments")

    # current command
    subparsers.add_parser("current", help="Show current environment")

    # login command
    login_parser = subparsers.add_parser("login", help="Force SSO login")
    login_parser.add_argument("--env", "-e", required=True,
                              choices=VALID_ENVS, help="Target environment")

    # update-kubeconfig command
    kubeconfig_parser = subparsers.add_parser("update-kubeconfig",
                                               help="Update kubeconfig for EKS cluster")
    kubeconfig_parser.add_argument("--env", "-e", required=True,
                                   choices=VALID_ENVS, help="Target environment")

    # Parse args, handling -- separator for kubectl
    if "--" in sys.argv:
        idx = sys.argv.index("--")
        main_args = sys.argv[1:idx]
        kubectl_args = sys.argv[idx + 1:]
    else:
        main_args = sys.argv[1:]
        kubectl_args = []

    args = parser.parse_args(main_args)

    if args.command == "kubectl":
        args.kubectl_args = kubectl_args

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Load configuration
    config = Config.load()

    if not config.sso_start_url and args.command not in ["list", "status"]:
        print("Error: AWS SSO not configured")
        print()
        print("Set up .credentials file with:")
        print("  AWS_SSO_START_URL - Your SSO portal URL")
        print("  AWS_SSO_REGION - SSO region")
        print()
        print("Example:")
        print('  export AWS_SSO_START_URL="https://mycompany.awsapps.com/start"')
        print('  export AWS_SSO_REGION="us-east-1"')
        sys.exit(1)

    # Execute command
    commands = {
        "status": cmd_status,
        "switch": cmd_switch,
        "kubectl": cmd_kubectl,
        "list": cmd_list,
        "current": cmd_current,
        "login": cmd_login,
        "update-kubeconfig": cmd_update_kubeconfig,
    }

    commands[args.command](config, args)


if __name__ == "__main__":
    main()
