#!/usr/bin/env python3
"""
VPN Check - Verify VPN connectivity via DNS resolution

Checks if internal hostnames resolve, indicating VPN is connected.
Auto-prompts for configuration on first run.

Usage:
    # Check VPN status
    python check_vpn.py

    # Quiet mode for scripting
    python check_vpn.py --quiet

    # Force re-run setup
    python check_vpn.py --setup

Exit Codes:
    0 - VPN connected (hostname resolved)
    1 - VPN not connected (hostname did not resolve)
    2 - Configuration error (missing or invalid config)
"""

import argparse
import os
import re
import socket
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple, Dict


# =============================================================================
# Configuration
# =============================================================================

def get_config_path() -> Path:
    """Return path to user's .vpn-config file."""
    return Path.home() / ".claude" / "skills" / "vpn-check" / ".vpn-config"


def parse_config(config_path: Path) -> Dict[str, str]:
    """
    Parse .vpn-config file to extract settings.

    Args:
        config_path: Path to .vpn-config

    Returns:
        Dict of configuration values
    """
    config = {}
    content = config_path.read_text()

    # Pattern to match: export VAR_NAME="value"
    export_pattern = re.compile(r'^export\s+([A-Z_][A-Z0-9_]*)\s*=\s*"([^"]*)"', re.MULTILINE)

    for match in export_pattern.finditer(content):
        var_name, value = match.groups()
        config[var_name] = value

    return config


def load_config() -> Optional[Dict[str, str]]:
    """
    Load configuration from .vpn-config file.

    Returns:
        Config dict or None if file doesn't exist
    """
    config_path = get_config_path()

    if not config_path.exists():
        return None

    try:
        return parse_config(config_path)
    except Exception as e:
        print(f"Error reading config: {e}")
        return None


# =============================================================================
# Interactive Setup
# =============================================================================

def interactive_setup() -> Optional[Dict[str, str]]:
    """
    Prompt user for VPN check configuration.

    Returns:
        Config dict or None if cancelled
    """
    print("\n" + "=" * 60)
    print("  VPN Check - First Time Setup")
    print("=" * 60)
    print()
    print("This skill checks VPN connectivity by verifying that internal")
    print("hostnames can be resolved via DNS.")
    print()

    # Prompt for hostname
    while True:
        host = input("Internal hostname to check (e.g., internal.example.com): ").strip()
        if host:
            break
        print("  Hostname cannot be empty. Please try again.")

    # Prompt for expected IP (optional)
    print()
    print("Optional: Expected IP address for extra validation")
    print("  Leave empty to skip (any resolved IP will be accepted)")
    expected_ip = input("Expected IP address: ").strip()

    # Create config
    config = {
        "VPN_CHECK_HOST": host,
    }

    if expected_ip:
        config["VPN_CHECK_EXPECTED_IP"] = expected_ip

    # Write config file
    config_path = get_config_path()
    config_path.parent.mkdir(parents=True, exist_ok=True)

    config_content = f"""# VPN Check Configuration
# Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# DO NOT commit this file - it contains internal hostnames

# Primary internal hostname to check
export VPN_CHECK_HOST="{config['VPN_CHECK_HOST']}"
"""

    if expected_ip:
        config_content += f"""
# Expected IP address for validation
export VPN_CHECK_EXPECTED_IP="{expected_ip}"
"""

    config_content += """
# Optional: DNS resolution timeout in seconds (default: 5)
# export VPN_CHECK_TIMEOUT="5"

# Optional: Additional fallback hosts (comma-separated)
# export VPN_CHECK_FALLBACK_HOSTS="backup1.internal.com,backup2.internal.com"
"""

    try:
        config_path.write_text(config_content)
        os.chmod(config_path, 0o600)
        print()
        print(f"Config created: {config_path}")
        print("Permissions set to 600 (owner read/write only)")
        print()
        return config
    except Exception as e:
        print(f"\nError creating config: {e}")
        return None


# =============================================================================
# VPN Check
# =============================================================================

def check_dns_resolution(host: str, timeout: int = 5) -> Tuple[bool, str]:
    """
    Check if a hostname can be resolved via DNS.

    Args:
        host: Hostname to resolve
        timeout: Timeout in seconds

    Returns:
        (success, ip_or_error_message)
    """
    socket.setdefaulttimeout(timeout)
    try:
        ip = socket.gethostbyname(host)
        return True, ip
    except socket.gaierror as e:
        return False, f"Could not resolve: {host}"
    except socket.timeout:
        return False, f"DNS lookup timed out: {host}"
    except Exception as e:
        return False, str(e)


def check_vpn_status(config: Dict[str, str], quiet: bool = False) -> int:
    """
    Check VPN connectivity based on configuration.

    Args:
        config: Configuration dict
        quiet: Suppress output

    Returns:
        Exit code (0=connected, 1=not connected, 2=error)
    """
    host = config.get("VPN_CHECK_HOST")
    if not host:
        if not quiet:
            print("Error: VPN_CHECK_HOST not configured")
        return 2

    expected_ip = config.get("VPN_CHECK_EXPECTED_IP")
    timeout = int(config.get("VPN_CHECK_TIMEOUT", "5"))
    fallback_hosts = config.get("VPN_CHECK_FALLBACK_HOSTS", "")

    # Check primary host
    success, result = check_dns_resolution(host, timeout)

    if success:
        # Validate expected IP if configured
        if expected_ip and result != expected_ip:
            if not quiet:
                print(f"VPN Status: UNEXPECTED IP")
                print(f"  Host: {host}")
                print(f"  Got IP: {result}")
                print(f"  Expected: {expected_ip}")
                print()
                print("  DNS resolved but to unexpected IP.")
                print("  You may be connected to a different network.")
            return 1

        if not quiet:
            print(f"VPN Connected")
            print(f"  Host: {host}")
            print(f"  IP: {result}")
        return 0

    # Primary failed, try fallbacks
    if fallback_hosts:
        for fallback in fallback_hosts.split(","):
            fallback = fallback.strip()
            if not fallback:
                continue

            fb_success, fb_result = check_dns_resolution(fallback, timeout)
            if fb_success:
                if not quiet:
                    print(f"VPN Connected (via fallback)")
                    print(f"  Host: {fallback}")
                    print(f"  IP: {fb_result}")
                return 0

    # All checks failed
    if not quiet:
        print(f"VPN Not Connected")
        print(f"  {result}")
        print()
        print("  Please connect to your VPN and try again.")

    return 1


# =============================================================================
# Main
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Check VPN connectivity via DNS resolution",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exit Codes:
  0  VPN connected (hostname resolved)
  1  VPN not connected (hostname did not resolve)
  2  Configuration error

Examples:
  %(prog)s              # Check VPN status
  %(prog)s --quiet      # Quiet mode (exit code only)
  %(prog)s --setup      # Force re-run setup
        """
    )

    parser.add_argument(
        '--setup', action='store_true',
        help='Run interactive setup (even if config exists)'
    )
    parser.add_argument(
        '--quiet', '-q', action='store_true',
        help='Quiet mode - only return exit code'
    )
    parser.add_argument(
        '--timeout', type=int,
        help='DNS timeout in seconds (overrides config)'
    )

    args = parser.parse_args()

    # Run setup if requested or if no config exists
    config = load_config()

    if args.setup or config is None:
        if config is None and not args.quiet:
            print("No VPN configuration found.")
        config = interactive_setup()
        if config is None:
            sys.exit(2)

    # Override timeout if specified
    if args.timeout:
        config["VPN_CHECK_TIMEOUT"] = str(args.timeout)

    # Check VPN status
    exit_code = check_vpn_status(config, args.quiet)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
