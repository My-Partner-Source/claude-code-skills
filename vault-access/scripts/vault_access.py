#!/usr/bin/env python3
"""HashiCorp Vault secret retrieval with KV v1/v2 support.

Retrieve secrets from Vault with:
- Automatic KV version detection
- Token-based authentication
- Multiple output formats
- Secret masking for security
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from urllib.parse import urljoin

try:
    import requests
except ImportError:
    print("Error: requests library not installed")
    print("Install with: pip install requests")
    sys.exit(1)

# Constants
SKILL_DIR = Path(__file__).parent.parent
CREDENTIALS_FILE = SKILL_DIR / "references" / ".credentials"

# Credential file search paths (in priority order)
CREDENTIAL_PATHS = [
    CREDENTIALS_FILE,
    Path.home() / ".claude" / "skills" / "vault-access" / ".credentials",
    Path(".credentials"),
]


def load_credentials() -> dict:
    """Load Vault credentials from .credentials file or environment."""
    creds = {
        "addr": os.environ.get("VAULT_ADDR"),
        "token": os.environ.get("VAULT_TOKEN"),
        "namespace": os.environ.get("VAULT_NAMESPACE", ""),
        "skip_verify": os.environ.get("VAULT_SKIP_VERIFY", "false").lower() == "true",
        "kv_version": os.environ.get("VAULT_KV_VERSION", "auto"),
    }

    # Try to load from credentials file if env vars not set
    if not creds["addr"] or not creds["token"]:
        creds_file = None
        for path in CREDENTIAL_PATHS:
            if path.exists():
                creds_file = path
                break

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
                        key = match.group(1)
                        value = match.group(2)

                        if key == "VAULT_ADDR" and not creds["addr"]:
                            creds["addr"] = value
                        elif key == "VAULT_TOKEN" and not creds["token"]:
                            creds["token"] = value
                        elif key == "VAULT_NAMESPACE":
                            creds["namespace"] = value
                        elif key == "VAULT_SKIP_VERIFY":
                            creds["skip_verify"] = value.lower() == "true"
                        elif key == "VAULT_KV_VERSION":
                            creds["kv_version"] = value

    # Validate required credentials
    if not creds["addr"]:
        print("Error: VAULT_ADDR not configured")
        print("\nTo set up credentials:")
        print("  1. Copy .credentials.example to .credentials")
        print("  2. Fill in your Vault server URL and token")
        print("  3. Or run: /credential-setup vault-access")
        sys.exit(1)

    if not creds["token"]:
        print("Error: VAULT_TOKEN not configured")
        print("\nTo get a Vault token:")
        print("  - CLI: vault login && vault token create")
        print("  - UI: Log into Vault > Click user icon > Copy Token")
        sys.exit(1)

    # Normalize address (remove trailing slash)
    creds["addr"] = creds["addr"].rstrip("/")

    return creds


def make_request(creds: dict, method: str, path: str, data: dict = None) -> dict:
    """Make authenticated request to Vault API."""
    url = f"{creds['addr']}/v1/{path.lstrip('/')}"

    headers = {
        "X-Vault-Token": creds["token"],
        "Content-Type": "application/json",
    }

    if creds["namespace"]:
        headers["X-Vault-Namespace"] = creds["namespace"]

    verify = not creds["skip_verify"]

    try:
        if method == "GET":
            response = requests.get(url, headers=headers, verify=verify, timeout=10)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data, verify=verify, timeout=10)
        elif method == "LIST":
            # Vault uses LIST method or GET with list=true
            response = requests.request("LIST", url, headers=headers, verify=verify, timeout=10)
        else:
            raise ValueError(f"Unsupported method: {method}")

        return {
            "status_code": response.status_code,
            "data": response.json() if response.text else {},
            "ok": response.ok,
        }

    except requests.exceptions.SSLError as e:
        print(f"SSL Error: {e}")
        print("\nIf using self-signed certificates, set VAULT_SKIP_VERIFY=true")
        print("(Not recommended for production)")
        sys.exit(1)

    except requests.exceptions.ConnectionError as e:
        print(f"Connection Error: Could not connect to {creds['addr']}")
        print("\nPossible causes:")
        print("  - VPN not connected (run /vpn-check)")
        print("  - Incorrect VAULT_ADDR")
        print("  - Vault server is down")
        sys.exit(1)

    except requests.exceptions.Timeout:
        print("Error: Request timed out")
        print("Check network connectivity and Vault server status")
        sys.exit(1)


def get_secret(creds: dict, path: str, key: str = None, kv_version: str = "auto") -> dict:
    """Retrieve secret from Vault.

    Args:
        creds: Vault credentials
        path: Secret path (e.g., 'secret/myapp/database')
        key: Specific key to retrieve (optional)
        kv_version: KV engine version ('1', '2', or 'auto')

    Returns:
        dict with 'data' containing secret key-value pairs
    """
    # Determine KV version
    if kv_version == "auto":
        kv_version = creds.get("kv_version", "auto")

    # Parse path - extract mount point and secret path
    parts = path.strip("/").split("/")
    if len(parts) < 2:
        print(f"Error: Invalid secret path: {path}")
        print("Path should be like: secret/myapp/database")
        sys.exit(1)

    mount = parts[0]
    secret_path = "/".join(parts[1:])

    # Try KV v2 first (more common in modern Vault)
    if kv_version in ("auto", "2"):
        v2_path = f"{mount}/data/{secret_path}"
        result = make_request(creds, "GET", v2_path)

        if result["ok"]:
            # KV v2 response: data is nested under data.data
            data = result["data"].get("data", {}).get("data", {})
            if key:
                if key in data:
                    return {"data": {key: data[key]}, "version": "2"}
                else:
                    print(f"Error: Key '{key}' not found in secret")
                    print(f"Available keys: {', '.join(data.keys())}")
                    sys.exit(1)
            return {"data": data, "version": "2"}

        # If 404 and auto, try v1
        if kv_version == "auto" and result["status_code"] == 404:
            pass  # Fall through to v1
        elif result["status_code"] == 403:
            print("Error: Permission denied")
            print("Check that your token has read access to this path")
            sys.exit(1)
        elif result["status_code"] != 404:
            handle_error(result)

    # Try KV v1
    if kv_version in ("auto", "1"):
        result = make_request(creds, "GET", path)

        if result["ok"]:
            data = result["data"].get("data", {})
            if key:
                if key in data:
                    return {"data": {key: data[key]}, "version": "1"}
                else:
                    print(f"Error: Key '{key}' not found in secret")
                    print(f"Available keys: {', '.join(data.keys())}")
                    sys.exit(1)
            return {"data": data, "version": "1"}

        handle_error(result)

    return {"data": {}, "version": "unknown"}


def list_secrets(creds: dict, path: str, kv_version: str = "auto") -> list:
    """List secrets at a path.

    Args:
        creds: Vault credentials
        path: Path to list (e.g., 'secret/myapp/')

    Returns:
        List of secret names/paths
    """
    if kv_version == "auto":
        kv_version = creds.get("kv_version", "auto")

    parts = path.strip("/").split("/")
    mount = parts[0]
    list_path = "/".join(parts[1:]) if len(parts) > 1 else ""

    # Try KV v2 first
    if kv_version in ("auto", "2"):
        v2_path = f"{mount}/metadata/{list_path}".rstrip("/")
        result = make_request(creds, "LIST", v2_path)

        if result["ok"]:
            return result["data"].get("data", {}).get("keys", [])

        if kv_version == "auto" and result["status_code"] == 404:
            pass  # Fall through to v1
        elif result["status_code"] == 403:
            print("Error: Permission denied")
            print("Check that your token has list access to this path")
            sys.exit(1)
        elif result["status_code"] != 404:
            handle_error(result)

    # Try KV v1
    if kv_version in ("auto", "1"):
        result = make_request(creds, "LIST", path.rstrip("/"))

        if result["ok"]:
            return result["data"].get("data", {}).get("keys", [])

        handle_error(result)

    return []


def check_status(creds: dict) -> dict:
    """Check Vault connectivity and authentication status."""
    # Check seal status
    result = make_request(creds, "GET", "sys/seal-status")
    if not result["ok"]:
        return {"connected": False, "error": "Could not reach Vault"}

    seal_status = result["data"]

    # Check token validity
    token_result = make_request(creds, "GET", "auth/token/lookup-self")
    if not token_result["ok"]:
        return {
            "connected": True,
            "sealed": seal_status.get("sealed", False),
            "authenticated": False,
            "error": "Token invalid or expired",
        }

    token_info = token_result["data"].get("data", {})

    return {
        "connected": True,
        "sealed": seal_status.get("sealed", False),
        "authenticated": True,
        "token_accessor": token_info.get("accessor", ""),
        "token_policies": token_info.get("policies", []),
        "token_ttl": token_info.get("ttl", 0),
        "token_renewable": token_info.get("renewable", False),
    }


def handle_error(result: dict):
    """Handle Vault API error responses."""
    status = result["status_code"]
    data = result["data"]

    errors = data.get("errors", [])
    error_msg = "; ".join(errors) if errors else "Unknown error"

    if status == 400:
        print(f"Error: Bad request - {error_msg}")
    elif status == 403:
        print(f"Error: Permission denied - {error_msg}")
        print("Check that your token has the required permissions")
    elif status == 404:
        print("Error: Secret not found")
        print("Check that the path is correct")
    elif status == 500:
        print("Error: Vault internal error")
        print("Check Vault server logs for details")
    elif status == 503:
        print("Error: Vault is sealed")
        print("The Vault server needs to be unsealed by an administrator")
    else:
        print(f"Error ({status}): {error_msg}")

    sys.exit(1)


def mask_value(value: str, show: bool = False) -> str:
    """Mask secret value unless show is True."""
    if show:
        return value
    if len(value) <= 4:
        return "****"
    return value[:2] + "*" * (len(value) - 4) + value[-2:]


def format_table(data: dict, show: bool = False) -> str:
    """Format secret data as a table."""
    if not data:
        return "*No data*"

    lines = []
    max_key_len = max(len(k) for k in data.keys())

    for key, value in sorted(data.items()):
        masked = mask_value(str(value), show)
        lines.append(f"{key.ljust(max_key_len)}  {masked}")

    return "\n".join(lines)


def format_json_output(data: dict, show: bool = False) -> str:
    """Format secret data as JSON."""
    if show:
        return json.dumps(data, indent=2)
    else:
        masked = {k: mask_value(str(v)) for k, v in data.items()}
        return json.dumps(masked, indent=2)


def format_env(data: dict, show: bool = False) -> str:
    """Format secret data as environment variable exports."""
    lines = []
    for key, value in sorted(data.items()):
        env_key = key.upper().replace("-", "_").replace(".", "_")
        masked = mask_value(str(value), show)
        lines.append(f'export {env_key}="{masked}"')
    return "\n".join(lines)


def format_raw(data: dict, key: str = None) -> str:
    """Format as raw value (single key only)."""
    if len(data) == 1:
        return str(list(data.values())[0])
    elif key and key in data:
        return str(data[key])
    else:
        print("Error: --format raw requires a single key (use --key)")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Retrieve secrets from HashiCorp Vault.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s get secret/myapp/database
  %(prog)s get secret/myapp/database --key password
  %(prog)s get secret/myapp/database --show
  %(prog)s list secret/myapp/
  %(prog)s status
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Get command
    get_parser = subparsers.add_parser("get", help="Retrieve secret(s) from a path")
    get_parser.add_argument("path", help="Secret path (e.g., secret/myapp/database)")
    get_parser.add_argument("--key", "-k", help="Get specific key from secret")
    get_parser.add_argument(
        "--show", "-s", action="store_true", help="Show actual values (default: masked)"
    )
    get_parser.add_argument(
        "--format",
        "-f",
        choices=["table", "json", "env", "raw"],
        default="table",
        help="Output format (default: table)",
    )
    get_parser.add_argument("--kv-version", choices=["1", "2", "auto"], default="auto",
                            help="KV engine version (default: auto-detect)")
    get_parser.add_argument("--output", "-o", help="Write output to file")

    # List command
    list_parser = subparsers.add_parser("list", help="List secrets at a path")
    list_parser.add_argument("path", help="Path to list (e.g., secret/myapp/)")
    list_parser.add_argument("--kv-version", choices=["1", "2", "auto"], default="auto",
                             help="KV engine version (default: auto-detect)")

    # Status command
    subparsers.add_parser("status", help="Check Vault connectivity and auth status")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Load credentials
    creds = load_credentials()

    if args.command == "status":
        status = check_status(creds)

        print(f"\nVault Status: {creds['addr']}")
        print("-" * 50)

        if not status["connected"]:
            print(f"Connection: FAILED - {status.get('error', 'Unknown error')}")
            sys.exit(1)

        print(f"Connection: OK")
        print(f"Sealed: {'Yes (needs unseal)' if status['sealed'] else 'No'}")

        if status["sealed"]:
            print("\nVault is sealed. Contact an administrator to unseal.")
            sys.exit(1)

        if not status["authenticated"]:
            print(f"Authentication: FAILED - {status.get('error', 'Token invalid')}")
            sys.exit(1)

        print(f"Authentication: OK")
        print(f"Token Accessor: {status['token_accessor']}")
        print(f"Policies: {', '.join(status['token_policies'])}")

        ttl = status["token_ttl"]
        if ttl > 0:
            hours = ttl // 3600
            minutes = (ttl % 3600) // 60
            print(f"Token TTL: {hours}h {minutes}m remaining")
        else:
            print(f"Token TTL: No expiration")

        print(f"Renewable: {'Yes' if status['token_renewable'] else 'No'}")

    elif args.command == "get":
        result = get_secret(creds, args.path, args.key, args.kv_version)
        data = result["data"]

        if not data:
            print("No data found at this path")
            sys.exit(1)

        # Format output
        if args.format == "table":
            output = format_table(data, args.show)
        elif args.format == "json":
            output = format_json_output(data, args.show)
        elif args.format == "env":
            output = format_env(data, args.show)
        elif args.format == "raw":
            output = format_raw(data, args.key)

        if args.output:
            with open(args.output, "w") as f:
                f.write(output)
            print(f"Output written to: {args.output}")
        else:
            print(output)

    elif args.command == "list":
        secrets = list_secrets(creds, args.path, args.kv_version)

        if not secrets:
            print("No secrets found at this path")
            sys.exit(0)

        print(f"\nSecrets at {args.path}:")
        print("-" * 40)
        for secret in sorted(secrets):
            # Directories end with /
            prefix = "[dir] " if secret.endswith("/") else "      "
            print(f"{prefix}{secret}")
        print(f"\n({len(secrets)} items)")


if __name__ == "__main__":
    main()
