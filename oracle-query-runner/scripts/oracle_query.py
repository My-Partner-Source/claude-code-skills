#!/usr/bin/env python3
"""Oracle Query Runner with environment switching and safety checks.

Execute Oracle SQL queries against DEV/QA/UAT/PROD environments with:
- Automatic credential loading per environment
- Write operation detection and confirmation
- Extra PROD safety warnings
- Markdown table output formatting
"""

import argparse
import csv
import io
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

# Venv auto-detection and re-exec
# If script is called with system Python instead of venv Python, re-exec with venv
SKILL_DIR = Path(__file__).resolve().parent.parent
_VENV_DIR = SKILL_DIR / ".venv"
_VENV_PYTHON = _VENV_DIR / "bin" / "python3"


def _is_running_in_venv() -> bool:
    """Check if we're running inside the skill's virtual environment."""
    if not _VENV_DIR.exists():
        return False
    # Resolve paths to handle symlinks
    venv_path = _VENV_DIR.resolve()
    prefix_path = Path(sys.prefix).resolve()
    return str(prefix_path).startswith(str(venv_path))


if not _is_running_in_venv():
    if _VENV_PYTHON.exists():
        # Venv exists but script called with wrong Python - re-exec with venv Python
        os.execv(str(_VENV_PYTHON), [str(_VENV_PYTHON)] + sys.argv)
    else:
        # Venv doesn't exist - prompt to run setup
        print("Error: Virtual environment not found.")
        print(f"Run setup first: cd {SKILL_DIR} && bash setup.sh")
        sys.exit(1)

try:
    import oracledb
except ImportError:
    print("Error: oracledb not installed")
    print("Install with: pip install oracledb")
    sys.exit(1)

# Constants
CREDENTIALS_FILE = SKILL_DIR / "references" / ".credentials"
VALID_ENVS = ["DEV", "QA", "UAT", "PROD"]

# Patterns for detecting write operations
WRITE_PATTERNS = [
    r"^\s*INSERT\b",
    r"^\s*UPDATE\b",
    r"^\s*DELETE\b",
    r"^\s*DROP\b",
    r"^\s*ALTER\b",
    r"^\s*TRUNCATE\b",
    r"^\s*CREATE\b",
    r"^\s*GRANT\b",
    r"^\s*REVOKE\b",
    r"^\s*MERGE\b",
    r"^\s*REPLACE\b",
]


def is_write_query(query: str) -> bool:
    """Detect if query modifies data."""
    query_upper = query.upper().strip()
    # Remove comments
    query_upper = re.sub(r"--.*$", "", query_upper, flags=re.MULTILINE)
    query_upper = re.sub(r"/\*.*?\*/", "", query_upper, flags=re.DOTALL)
    query_upper = query_upper.strip()

    return any(re.search(pattern, query_upper, re.IGNORECASE) for pattern in WRITE_PATTERNS)


def has_row_limit(query: str) -> bool:
    """Check if SELECT query has a row limit clause."""
    query_upper = query.upper()
    # Check for various Oracle row limiting patterns
    return any(pattern in query_upper for pattern in [
        "ROWNUM",
        "FETCH FIRST",
        "FETCH NEXT",
        "SAMPLE(",
        "WHERE ROWID",
    ])


def load_credentials(env: str) -> dict:
    """Load credentials for specified environment from .credentials file."""
    if not CREDENTIALS_FILE.exists():
        print(f"Error: Credentials file not found: {CREDENTIALS_FILE}")
        print("\nTo set up credentials:")
        print("  1. Copy .credentials.example to .credentials")
        print("  2. Fill in your database connection details")
        print("  3. Or run: /credential-setup oracle-query-runner")
        sys.exit(1)

    prefix = f"ORACLE_{env.upper()}_"
    creds = {}

    with open(CREDENTIALS_FILE) as f:
        for line in f:
            line = line.strip()
            # Skip comments and empty lines
            if not line or line.startswith("#"):
                continue

            # Parse: export ORACLE_DEV_HOST="value" or ORACLE_DEV_HOST="value"
            if prefix in line:
                # Handle both with and without 'export'
                line = line.replace("export ", "")
                match = re.match(r'(\w+)=["\']?([^"\']*)["\']?', line)
                if match:
                    full_key = match.group(1)
                    value = match.group(2)
                    # Extract the key name (e.g., HOST from ORACLE_DEV_HOST)
                    key = full_key.replace(prefix, "").lower()
                    creds[key] = value

    required = ["host", "user", "password", "service"]
    missing = [k for k in required if k not in creds or not creds[k]]
    if missing:
        print(f"Error: Missing or empty credentials for {env}: {missing}")
        print(f"\nCheck your .credentials file has all ORACLE_{env}_* values set.")
        sys.exit(1)

    # Default port if not specified
    if "port" not in creds or not creds["port"]:
        creds["port"] = "1521"

    return creds


def format_markdown_table(columns: list, rows: list, max_width: int = 50) -> str:
    """Format results as a markdown table."""
    if not rows:
        return "*No results*"

    # Convert all cells to strings, handling None and truncating long values
    def format_cell(value):
        if value is None:
            return "NULL"
        s = str(value)
        if len(s) > max_width:
            return s[: max_width - 3] + "..."
        return s

    str_rows = [[format_cell(cell) for cell in row] for row in rows]

    # Calculate column widths
    widths = [len(str(c)) for c in columns]
    for row in str_rows:
        for i, cell in enumerate(row):
            if i < len(widths):
                widths[i] = max(widths[i], len(cell))

    # Build table
    lines = []

    # Header
    header_cells = [str(c).ljust(widths[i]) for i, c in enumerate(columns)]
    lines.append("| " + " | ".join(header_cells) + " |")

    # Separator
    lines.append("|" + "|".join("-" * (w + 2) for w in widths) + "|")

    # Data rows
    for row in str_rows:
        cells = [cell.ljust(widths[i]) if i < len(widths) else cell for i, cell in enumerate(row)]
        lines.append("| " + " | ".join(cells) + " |")

    return "\n".join(lines)


def format_csv(columns: list, rows: list) -> str:
    """Format results as CSV."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(columns)
    writer.writerows(rows)
    return output.getvalue()


def format_json(columns: list, rows: list) -> str:
    """Format results as JSON."""
    result = []
    for row in rows:
        result.append(dict(zip(columns, [str(v) if v is not None else None for v in row])))
    return json.dumps(result, indent=2)


def confirm_write(query: str, env: str) -> bool:
    """Prompt for confirmation before write operations."""
    print("\n" + "=" * 60)

    if env == "PROD":
        print("  PRODUCTION WRITE DETECTED  ")
        print("=" * 60)
        print("\nThis will modify the PRODUCTION database!")
    else:
        print(f"  WRITE OPERATION on {env}  ")
        print("=" * 60)

    print("\nQuery:")
    print("-" * 40)
    print(query)
    print("-" * 40)

    if env == "PROD":
        print('\nType "PROD" to confirm, or anything else to cancel:')
        response = input("> ").strip()
        return response == "PROD"
    else:
        print("\nProceed? [y/N]: ", end="")
        response = input().strip().lower()
        return response in ("y", "yes")


def execute_query(creds: dict, query: str, env: str) -> tuple:
    """Execute query and return (columns, rows) or (None, rowcount)."""
    conn = None
    cursor = None

    try:
        # Build DSN (Data Source Name) using Easy Connect format
        dsn = f"{creds['host']}:{creds['port']}/{creds['service']}"

        conn = oracledb.connect(
            user=creds["user"],
            password=creds["password"],
            dsn=dsn
        )

        cursor = conn.cursor()
        cursor.execute(query)

        if cursor.description:
            # SELECT query - has results
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            return columns, rows, None
        else:
            # Write query - return rowcount
            conn.commit()
            return None, None, cursor.rowcount

    except oracledb.Error as e:
        error = e.args[0]
        print(f"\nOracle Error: {error}")

        # Provide helpful suggestions based on error type
        error_str = str(error)
        if "ORA-01017" in error_str:
            print(f"\nInvalid username/password. Check your credentials for {env} environment.")
        elif "ORA-12541" in error_str:
            print("\nConnection failed - TNS listener not available.")
            print("Possible causes:")
            print("  - VPN not connected (run /vpn-check)")
            print("  - Incorrect host/port")
            print("  - Database server is down")
        elif "ORA-12514" in error_str:
            print(f"\nService name not found. Check ORACLE_{env}_SERVICE in credentials.")
        elif "ORA-12154" in error_str:
            print(f"\nTNS could not resolve connect identifier. Check ORACLE_{env}_SERVICE.")
        elif "ORA-12170" in error_str:
            print("\nConnection timeout. Check VPN connectivity and host/port.")
        elif "ORA-28000" in error_str:
            print(f"\nAccount locked. Contact DBA to unlock the {env} database account.")
        elif "ORA-01034" in error_str:
            print("\nOracle not available. The database instance may be down.")
        sys.exit(1)

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def prompt_for_env() -> str:
    """Prompt user to select an environment."""
    print("\nWhich environment should I run this query against?")
    for i, env in enumerate(VALID_ENVS, 1):
        warning = " (CAUTION)" if env == "PROD" else ""
        print(f"  {i}. {env}{warning}")
    print("\nSelect [1-4]: ", end="")

    try:
        choice = int(input().strip())
        if 1 <= choice <= 4:
            return VALID_ENVS[choice - 1]
    except (ValueError, IndexError):
        pass

    print("Invalid selection. Aborting.")
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Execute Oracle SQL queries with environment switching and safety checks.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --env DEV --query "SELECT * FROM users WHERE ROWNUM <= 10"
  %(prog)s --env QA --query "SELECT table_name FROM user_tables"
  %(prog)s --env UAT -q "SELECT * FROM v$version"
  %(prog)s --env PROD -q "SELECT COUNT(*) FROM orders" --yes
        """,
    )

    parser.add_argument(
        "--env",
        "-e",
        choices=VALID_ENVS,
        help="Target environment: DEV, QA, UAT, or PROD",
    )

    parser.add_argument(
        "--query",
        "-q",
        help="SQL query to execute. If omitted, prompts for input.",
    )

    parser.add_argument(
        "--format",
        "-f",
        choices=["markdown", "csv", "json"],
        default="markdown",
        help="Output format (default: markdown)",
    )

    parser.add_argument(
        "--output",
        "-o",
        help="Write results to file instead of stdout",
    )

    parser.add_argument(
        "--yes",
        "-y",
        action="store_true",
        help="Skip confirmation for SELECT queries (writes still require confirmation)",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would execute without running",
    )

    parser.add_argument(
        "--show-config",
        action="store_true",
        help="Show loaded configuration (without password)",
    )

    args = parser.parse_args()

    # Get environment
    env = args.env
    if not env:
        env = prompt_for_env()

    # Load credentials
    creds = load_credentials(env)

    # Show config if requested
    if args.show_config:
        print(f"\nConfiguration for {env}:")
        print(f"  Host:     {creds['host']}")
        print(f"  Port:     {creds.get('port', '1521')}")
        print(f"  User:     {creds['user']}")
        print(f"  Service:  {creds['service']}")
        print(f"  Password: {'*' * len(creds['password'])}")
        if not args.query:
            sys.exit(0)

    # Get query
    query = args.query
    if not query:
        print(f"\nConnected to: {env} ({creds['host']}/{creds['service']})")
        print("Enter your SQL query (end with semicolon and press Enter):")
        lines = []
        while True:
            line = input()
            lines.append(line)
            if line.strip().endswith(";"):
                break
        query = "\n".join(lines)

    query = query.strip()
    if not query:
        print("Error: Empty query")
        sys.exit(1)

    # Remove trailing semicolon for oracledb
    if query.endswith(";"):
        query = query[:-1]

    # Check for write operations
    is_write = is_write_query(query)

    # Dry run
    if args.dry_run:
        print(f"\n[DRY RUN] Would execute on {env}:")
        print("-" * 40)
        print(query)
        print("-" * 40)
        print(f"Type: {'WRITE' if is_write else 'READ'}")
        sys.exit(0)

    # Warn about missing row limit for SELECTs
    if not is_write and not has_row_limit(query) and query.upper().strip().startswith("SELECT"):
        if not args.yes:
            print(f"\nWarning: SELECT query without ROWNUM/FETCH clause on {env}")
            print("Consider adding ROWNUM <= N or FETCH FIRST N ROWS to avoid fetching too many rows.")
            print("Continue anyway? [y/N]: ", end="")
            if input().strip().lower() not in ("y", "yes"):
                print("Aborted.")
                sys.exit(0)

    # Confirm write operations
    if is_write:
        if not confirm_write(query, env):
            print("\nAborted.")
            sys.exit(0)

    # Execute
    print(f"\nExecuting on {env}...", end="", flush=True)
    columns, rows, rowcount = execute_query(creds, query, env)
    print(" done.\n")

    # Format output
    if columns is not None:
        # SELECT results
        row_count = len(rows)

        if args.format == "markdown":
            output = format_markdown_table(columns, rows)
        elif args.format == "csv":
            output = format_csv(columns, rows)
        elif args.format == "json":
            output = format_json(columns, rows)

        if args.output:
            with open(args.output, "w") as f:
                f.write(output)
            print(f"Results written to: {args.output}")
            print(f"Rows: {row_count}")
        else:
            print(output)
            print(f"\n({row_count} row{'s' if row_count != 1 else ''})")

    else:
        # Write operation
        print(f"Query OK, {rowcount} row{'s' if rowcount != 1 else ''} affected.")


if __name__ == "__main__":
    main()
