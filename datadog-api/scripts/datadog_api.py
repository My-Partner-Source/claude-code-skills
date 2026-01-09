#!/usr/bin/env python3
"""
Datadog API Helper

A utility script for querying Datadog metrics, monitors, dashboards, and events.
Provides read-only access to Datadog observability data.

Usage:
    python datadog_api.py monitors [--status STATUS] [--tag TAG]
    python datadog_api.py query --metric METRIC [--from HOURS] [--tags TAGS]
    python datadog_api.py dashboards [--filter NAME]
    python datadog_api.py events [--from HOURS] [--tags TAGS]
    python datadog_api.py monitor-info --id ID
    python datadog_api.py dashboard-info --id ID

Environment Variables:
    DD_API_KEY  - Datadog API key (required)
    DD_APP_KEY  - Datadog Application key (required)
    DD_SITE     - Datadog site (optional, default: datadoghq.com)

Examples:
    # List alerting monitors
    python datadog_api.py monitors --status alerting

    # Query CPU metric
    python datadog_api.py query --metric system.cpu.user --from 2 --tags host:prod-web-01

    # List dashboards
    python datadog_api.py dashboards --filter production

    # Get recent events
    python datadog_api.py events --from 24 --tags service:api
"""

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urlencode

# Check for requests library
try:
    import requests
except ImportError:
    print("Error: 'requests' library is required. Install with: pip install requests")
    sys.exit(1)


# Constants
DEFAULT_SITE = "datadoghq.com"
MAX_RETRIES = 3
RETRY_DELAY = 2

# Datadog site to API base URL mapping
SITE_API_URLS = {
    "datadoghq.com": "https://api.datadoghq.com",
    "us3.datadoghq.com": "https://api.us3.datadoghq.com",
    "us5.datadoghq.com": "https://api.us5.datadoghq.com",
    "datadoghq.eu": "https://api.datadoghq.eu",
    "ap1.datadoghq.com": "https://api.ap1.datadoghq.com",
    "ddog-gov.com": "https://api.ddog-gov.com",
}


def load_credentials_from_file() -> Dict[str, str]:
    """
    Load credentials from .credentials file.

    Searches in order:
    1. datadog-api/references/.credentials (skill location)
    2. ./references/.credentials (current directory)
    3. ./.credentials (current directory)

    Returns dict of environment variables found.
    """
    credentials = {}

    # Determine script location for relative path resolution
    script_dir = Path(__file__).resolve().parent
    skill_dir = script_dir.parent

    # Potential credential file locations
    search_paths = [
        skill_dir / "references" / ".credentials",
        Path("references") / ".credentials",
        Path(".credentials"),
    ]

    for cred_path in search_paths:
        if cred_path.exists():
            try:
                with open(cred_path, "r") as f:
                    for line in f:
                        line = line.strip()
                        # Parse bash export statements: export VAR="value"
                        match = re.match(r'^export\s+([A-Z_]+)="([^"]*)"', line)
                        if match:
                            var_name, var_value = match.groups()
                            if var_name.startswith("DD_") and var_value:
                                credentials[var_name] = var_value
                if credentials:
                    return credentials
            except (IOError, OSError):
                continue

    return credentials


def get_credentials(args: argparse.Namespace) -> tuple:
    """
    Get credentials from CLI args, environment, or .credentials file.

    Priority:
    1. CLI arguments (--api-key, --app-key, --site)
    2. Environment variables (DD_API_KEY, DD_APP_KEY, DD_SITE)
    3. .credentials file

    Returns tuple of (api_key, app_key, site)
    """
    # Load from .credentials file first (lowest priority)
    file_creds = load_credentials_from_file()

    # Resolve with priority: CLI > env > file
    api_key = (
        getattr(args, "api_key", None) or
        os.environ.get("DD_API_KEY") or
        file_creds.get("DD_API_KEY")
    )

    app_key = (
        getattr(args, "app_key", None) or
        os.environ.get("DD_APP_KEY") or
        file_creds.get("DD_APP_KEY")
    )

    site = (
        getattr(args, "site", None) or
        os.environ.get("DD_SITE") or
        file_creds.get("DD_SITE") or
        DEFAULT_SITE
    )

    return api_key, app_key, site


class DatadogClient:
    """Client for interacting with the Datadog API."""

    def __init__(self, api_key: str, app_key: str, site: str = DEFAULT_SITE):
        """
        Initialize the Datadog client.

        Args:
            api_key: Datadog API key
            app_key: Datadog Application key
            site: Datadog site (e.g., datadoghq.com, datadoghq.eu)
        """
        self.api_key = api_key
        self.app_key = app_key
        self.site = site
        self.base_url = SITE_API_URLS.get(site, f"https://api.{site}")

        self.session = requests.Session()
        self.session.headers.update({
            "DD-API-KEY": api_key,
            "DD-APPLICATION-KEY": app_key,
            "Content-Type": "application/json",
        })

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """
        Make an API request with retry logic.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (e.g., /api/v1/monitor)
            params: Query parameters
            data: Request body data

        Returns:
            API response as dictionary

        Raises:
            requests.RequestException: On API error after retries
        """
        url = f"{self.base_url}{endpoint}"

        for attempt in range(MAX_RETRIES):
            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    params=params,
                    json=data,
                    timeout=30,
                )

                if response.status_code == 429:
                    # Rate limited, wait and retry
                    retry_after = int(response.headers.get("X-RateLimit-Reset", RETRY_DELAY))
                    print(f"Rate limited. Waiting {retry_after}s...", file=sys.stderr)
                    time.sleep(retry_after)
                    continue

                response.raise_for_status()
                return response.json() if response.text else {}

            except requests.RequestException as e:
                if attempt < MAX_RETRIES - 1:
                    print(f"Request failed, retrying ({attempt + 1}/{MAX_RETRIES})...", file=sys.stderr)
                    time.sleep(RETRY_DELAY)
                else:
                    raise

        return {}

    def list_monitors(
        self,
        status: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> List[Dict]:
        """
        List monitors with optional filtering.

        Args:
            status: Filter by status (Alert, Warn, OK, No Data)
            tags: Filter by tags

        Returns:
            List of monitor dictionaries
        """
        params = {}

        if tags:
            params["monitor_tags"] = ",".join(tags)

        monitors = self._make_request("GET", "/api/v1/monitor", params=params)

        if not isinstance(monitors, list):
            monitors = []

        # Filter by status if specified
        if status:
            status_map = {
                "alerting": "Alert",
                "alert": "Alert",
                "warn": "Warn",
                "warning": "Warn",
                "ok": "OK",
                "no_data": "No Data",
                "nodata": "No Data",
            }
            target_status = status_map.get(status.lower(), status)
            monitors = [m for m in monitors if m.get("overall_state") == target_status]

        return monitors

    def get_monitor(self, monitor_id: int) -> Dict:
        """
        Get details for a specific monitor.

        Args:
            monitor_id: The monitor ID

        Returns:
            Monitor details dictionary
        """
        return self._make_request("GET", f"/api/v1/monitor/{monitor_id}")

    def query_metrics(
        self,
        metric: str,
        from_hours: int = 1,
        tags: Optional[str] = None,
    ) -> Dict:
        """
        Query time-series metrics.

        Args:
            metric: Metric name (e.g., system.cpu.user)
            from_hours: Hours ago to start query
            tags: Tag filter string (e.g., host:prod-web-01)

        Returns:
            Metrics query result
        """
        now = int(time.time())
        from_ts = now - (from_hours * 3600)

        # Build query string
        query = metric
        if tags:
            query = f"{metric}{{{tags}}}"

        params = {
            "from": from_ts,
            "to": now,
            "query": query,
        }

        return self._make_request("GET", "/api/v1/query", params=params)

    def list_dashboards(self, filter_name: Optional[str] = None) -> List[Dict]:
        """
        List dashboards with optional name filter.

        Args:
            filter_name: Filter dashboards by name (case-insensitive contains)

        Returns:
            List of dashboard summaries
        """
        params = {}
        if filter_name:
            params["filter[shared]"] = "false"

        result = self._make_request("GET", "/api/v1/dashboard", params=params)
        dashboards = result.get("dashboards", [])

        if filter_name:
            filter_lower = filter_name.lower()
            dashboards = [
                d for d in dashboards
                if filter_lower in d.get("title", "").lower()
            ]

        return dashboards

    def get_dashboard(self, dashboard_id: str) -> Dict:
        """
        Get dashboard definition.

        Args:
            dashboard_id: Dashboard ID

        Returns:
            Dashboard definition
        """
        return self._make_request("GET", f"/api/v1/dashboard/{dashboard_id}")

    def list_events(
        self,
        from_hours: int = 24,
        tags: Optional[str] = None,
        priority: Optional[str] = None,
    ) -> List[Dict]:
        """
        List events with filtering.

        Args:
            from_hours: Hours ago to search
            tags: Tag filter
            priority: Event priority (normal, low)

        Returns:
            List of events
        """
        now = int(time.time())
        from_ts = now - (from_hours * 3600)

        params = {
            "start": from_ts,
            "end": now,
        }

        if tags:
            params["tags"] = tags
        if priority:
            params["priority"] = priority

        result = self._make_request("GET", "/api/v1/events", params=params)
        return result.get("events", [])

    def validate(self) -> bool:
        """
        Validate API credentials.

        Returns:
            True if credentials are valid
        """
        try:
            self._make_request("GET", "/api/v1/validate")
            return True
        except requests.RequestException:
            return False


def format_monitors_table(monitors: List[Dict]) -> str:
    """Format monitors as a table."""
    if not monitors:
        return "No monitors found."

    lines = []
    lines.append("┌" + "─" * 78 + "┐")
    lines.append(f"│ {'Status':<8} │ {'Name':<35} │ {'Type':<10} │ {'Last Triggered':<16} │")
    lines.append("├" + "─" * 78 + "┤")

    for m in monitors:
        status = m.get("overall_state", "Unknown")[:8]
        name = m.get("name", "Unnamed")[:35]
        mon_type = m.get("type", "N/A")[:10]

        # Get last triggered time
        last_triggered = "N/A"
        if m.get("state", {}).get("groups"):
            for group_data in m["state"]["groups"].values():
                if group_data.get("last_triggered_ts"):
                    ts = group_data["last_triggered_ts"]
                    last_triggered = datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M")
                    break

        lines.append(f"│ {status:<8} │ {name:<35} │ {mon_type:<10} │ {last_triggered:<16} │")

    lines.append("└" + "─" * 78 + "┘")
    lines.append(f"\nTotal: {len(monitors)} monitor(s)")

    return "\n".join(lines)


def format_metrics_result(result: Dict, metric: str, from_hours: int, tags: Optional[str]) -> str:
    """Format metrics query result."""
    series = result.get("series", [])

    if not series:
        return f"No data found for metric: {metric}"

    lines = []
    lines.append(f"Metric: {metric}")
    if tags:
        lines.append(f"Tags: {tags}")
    lines.append(f"Time Range: Last {from_hours} hour(s)")
    lines.append("")

    for s in series:
        scope = s.get("scope", "all")
        pointlist = s.get("pointlist", [])

        if pointlist:
            values = [p[1] for p in pointlist if p[1] is not None]
            if values:
                lines.append(f"Scope: {scope}")
                lines.append(f"  Min: {min(values):.2f}")
                lines.append(f"  Max: {max(values):.2f}")
                lines.append(f"  Avg: {sum(values) / len(values):.2f}")
                lines.append(f"  Data Points: {len(values)}")
                lines.append("")

    return "\n".join(lines)


def format_dashboards_table(dashboards: List[Dict]) -> str:
    """Format dashboards as a table."""
    if not dashboards:
        return "No dashboards found."

    lines = []
    lines.append("┌" + "─" * 78 + "┐")
    lines.append(f"│ {'ID':<20} │ {'Title':<40} │ {'Author':<12} │")
    lines.append("├" + "─" * 78 + "┤")

    for d in dashboards:
        dash_id = d.get("id", "N/A")[:20]
        title = d.get("title", "Untitled")[:40]
        author = d.get("author_handle", "N/A")[:12]
        lines.append(f"│ {dash_id:<20} │ {title:<40} │ {author:<12} │")

    lines.append("└" + "─" * 78 + "┘")
    lines.append(f"\nTotal: {len(dashboards)} dashboard(s)")

    return "\n".join(lines)


def format_events_list(events: List[Dict]) -> str:
    """Format events as a list."""
    if not events:
        return "No events found."

    lines = []
    lines.append(f"Found {len(events)} event(s):\n")

    for e in events:
        timestamp = e.get("date_happened", 0)
        time_str = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
        title = e.get("title", "No title")
        source = e.get("source_type_name", "N/A")
        priority = e.get("priority", "normal")

        lines.append(f"[{time_str}] ({priority}) {source}: {title}")

        if e.get("text"):
            text_preview = e["text"][:100] + "..." if len(e["text"]) > 100 else e["text"]
            lines.append(f"  {text_preview}")
        lines.append("")

    return "\n".join(lines)


def cmd_monitors(client: DatadogClient, args: argparse.Namespace) -> int:
    """Handle monitors command."""
    tags = args.tag.split(",") if args.tag else None

    try:
        monitors = client.list_monitors(status=args.status, tags=tags)
        print(format_monitors_table(monitors))
        return 0
    except requests.RequestException as e:
        print(f"Error listing monitors: {e}", file=sys.stderr)
        return 1


def cmd_query(client: DatadogClient, args: argparse.Namespace) -> int:
    """Handle query command."""
    if not args.metric:
        print("Error: --metric is required", file=sys.stderr)
        return 1

    try:
        result = client.query_metrics(
            metric=args.metric,
            from_hours=args.from_hours,
            tags=args.tags,
        )
        print(format_metrics_result(result, args.metric, args.from_hours, args.tags))
        return 0
    except requests.RequestException as e:
        print(f"Error querying metrics: {e}", file=sys.stderr)
        return 1


def cmd_dashboards(client: DatadogClient, args: argparse.Namespace) -> int:
    """Handle dashboards command."""
    try:
        dashboards = client.list_dashboards(filter_name=args.filter)
        print(format_dashboards_table(dashboards))
        return 0
    except requests.RequestException as e:
        print(f"Error listing dashboards: {e}", file=sys.stderr)
        return 1


def cmd_events(client: DatadogClient, args: argparse.Namespace) -> int:
    """Handle events command."""
    try:
        events = client.list_events(
            from_hours=args.from_hours,
            tags=args.tags,
            priority=args.priority,
        )
        print(format_events_list(events))
        return 0
    except requests.RequestException as e:
        print(f"Error listing events: {e}", file=sys.stderr)
        return 1


def cmd_monitor_info(client: DatadogClient, args: argparse.Namespace) -> int:
    """Handle monitor-info command."""
    if not args.id:
        print("Error: --id is required", file=sys.stderr)
        return 1

    try:
        monitor = client.get_monitor(int(args.id))
        print(json.dumps(monitor, indent=2))
        return 0
    except requests.RequestException as e:
        print(f"Error getting monitor: {e}", file=sys.stderr)
        return 1


def cmd_dashboard_info(client: DatadogClient, args: argparse.Namespace) -> int:
    """Handle dashboard-info command."""
    if not args.id:
        print("Error: --id is required", file=sys.stderr)
        return 1

    try:
        dashboard = client.get_dashboard(args.id)
        print(json.dumps(dashboard, indent=2))
        return 0
    except requests.RequestException as e:
        print(f"Error getting dashboard: {e}", file=sys.stderr)
        return 1


def main():
    """Main entry point."""
    # Parent parser for common auth arguments
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument("--api-key", help="Datadog API key")
    parent_parser.add_argument("--app-key", help="Datadog Application key")
    parent_parser.add_argument("--site", help="Datadog site (e.g., datadoghq.com)")

    # Main parser
    parser = argparse.ArgumentParser(
        description="Datadog API Helper - Query metrics, monitors, dashboards, and events",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s monitors --status alerting
  %(prog)s query --metric system.cpu.user --from 2
  %(prog)s dashboards --filter production
  %(prog)s events --from 24 --tags service:api
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # monitors command
    monitors_parser = subparsers.add_parser(
        "monitors",
        parents=[parent_parser],
        help="List monitors",
    )
    monitors_parser.add_argument(
        "--status",
        choices=["alerting", "warn", "ok", "no_data", "all"],
        help="Filter by status",
    )
    monitors_parser.add_argument("--tag", help="Filter by tag (comma-separated)")

    # query command
    query_parser = subparsers.add_parser(
        "query",
        parents=[parent_parser],
        help="Query metrics",
    )
    query_parser.add_argument("--metric", "-m", required=True, help="Metric name")
    query_parser.add_argument(
        "--from",
        dest="from_hours",
        type=int,
        default=1,
        help="Hours ago to start (default: 1)",
    )
    query_parser.add_argument("--tags", "-t", help="Tag filter (e.g., host:prod-web-01)")

    # dashboards command
    dashboards_parser = subparsers.add_parser(
        "dashboards",
        parents=[parent_parser],
        help="List dashboards",
    )
    dashboards_parser.add_argument("--filter", "-f", help="Filter by name")

    # events command
    events_parser = subparsers.add_parser(
        "events",
        parents=[parent_parser],
        help="List events",
    )
    events_parser.add_argument(
        "--from",
        dest="from_hours",
        type=int,
        default=24,
        help="Hours ago to search (default: 24)",
    )
    events_parser.add_argument("--tags", "-t", help="Tag filter")
    events_parser.add_argument(
        "--priority",
        choices=["normal", "low"],
        help="Filter by priority",
    )

    # monitor-info command
    monitor_info_parser = subparsers.add_parser(
        "monitor-info",
        parents=[parent_parser],
        help="Get monitor details",
    )
    monitor_info_parser.add_argument("--id", required=True, help="Monitor ID")

    # dashboard-info command
    dashboard_info_parser = subparsers.add_parser(
        "dashboard-info",
        parents=[parent_parser],
        help="Get dashboard definition",
    )
    dashboard_info_parser.add_argument("--id", required=True, help="Dashboard ID")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    # Get credentials
    api_key, app_key, site = get_credentials(args)

    if not api_key or not app_key:
        print("Error: Missing credentials.", file=sys.stderr)
        print("", file=sys.stderr)
        print("Set credentials via:", file=sys.stderr)
        print("  1. Environment variables: DD_API_KEY, DD_APP_KEY", file=sys.stderr)
        print("  2. .credentials file in datadog-api/references/", file=sys.stderr)
        print("  3. CLI arguments: --api-key, --app-key", file=sys.stderr)
        print("", file=sys.stderr)
        print("To create .credentials file:", file=sys.stderr)
        print("  cp datadog-api/references/.credentials.example datadog-api/references/.credentials", file=sys.stderr)
        print("  # Edit with your values", file=sys.stderr)
        return 1

    # Create client
    client = DatadogClient(api_key, app_key, site)

    # Validate credentials
    if not client.validate():
        print("Error: Invalid credentials or unable to reach Datadog API.", file=sys.stderr)
        print(f"Site: {site}", file=sys.stderr)
        print(f"API URL: {client.base_url}", file=sys.stderr)
        return 1

    # Route to command handler
    command_handlers = {
        "monitors": cmd_monitors,
        "query": cmd_query,
        "dashboards": cmd_dashboards,
        "events": cmd_events,
        "monitor-info": cmd_monitor_info,
        "dashboard-info": cmd_dashboard_info,
    }

    handler = command_handlers.get(args.command)
    if handler:
        return handler(client, args)
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
