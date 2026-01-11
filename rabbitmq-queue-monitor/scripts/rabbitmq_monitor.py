#!/usr/bin/env python3
"""
RabbitMQ Queue Monitor Script

Monitor RabbitMQ queues and health across LOCAL/DEV/QA/UAT/PROD environments
using the RabbitMQ Management HTTP API.

Usage:
    # Health and overview
    rabbitmq_monitor.py --env DEV overview
    rabbitmq_monitor.py --env DEV health
    rabbitmq_monitor.py --env DEV nodes

    # Queue operations
    rabbitmq_monitor.py --env DEV queues
    rabbitmq_monitor.py --env DEV queues --backlog
    rabbitmq_monitor.py --env DEV queues --filter "order"
    rabbitmq_monitor.py --env DEV queue my-queue-name
    rabbitmq_monitor.py --env DEV queue my-queue-name --rates

    # Connections and channels
    rabbitmq_monitor.py --env DEV connections
    rabbitmq_monitor.py --env DEV channels
    rabbitmq_monitor.py --env DEV consumers

    # Exchanges and bindings
    rabbitmq_monitor.py --env DEV exchanges
    rabbitmq_monitor.py --env DEV bindings my-queue-name
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from urllib.parse import quote

# Auto-reexec with venv if needed
SCRIPT_DIR = Path(__file__).resolve().parent.parent
VENV_PYTHON = SCRIPT_DIR / ".venv" / "bin" / "python3"

if VENV_PYTHON.exists() and sys.executable != str(VENV_PYTHON):
    os.execv(str(VENV_PYTHON), [str(VENV_PYTHON), __file__] + sys.argv[1:])

try:
    import requests
    from requests.auth import HTTPBasicAuth
except ImportError:
    print("Error: requests package not installed.")
    print("Run setup first: cd ~/.claude/skills/rabbitmq-queue-monitor && bash setup.sh")
    sys.exit(1)

# Valid environments
ENVIRONMENTS = ["LOCAL", "DEV", "QA", "UAT", "PROD"]


def load_credentials_from_file() -> dict:
    """Load credentials from .credentials file."""
    credentials = {}

    # Search locations for .credentials file
    search_paths = [
        SCRIPT_DIR / "references" / ".credentials",
        Path.cwd() / "references" / ".credentials",
        Path.cwd() / ".credentials",
        Path.home() / ".claude" / "skills" / "rabbitmq-queue-monitor" / "references" / ".credentials",
    ]

    credentials_file = None
    for path in search_paths:
        if path.exists():
            credentials_file = path
            break

    if not credentials_file:
        return credentials

    # Parse bash export statements
    pattern = r'^export\s+([A-Z_]+)="([^"]*)"'
    try:
        with open(credentials_file, "r") as f:
            for line in f:
                line = line.strip()
                match = re.match(pattern, line)
                if match:
                    key, value = match.groups()
                    credentials[key] = value
    except Exception:
        pass

    return credentials


def get_env_config(env: str, credentials: dict) -> dict:
    """Get configuration for specific environment."""
    env_upper = env.upper()

    config = {
        "host": credentials.get(f"RABBITMQ_{env_upper}_HOST") or os.environ.get(f"RABBITMQ_{env_upper}_HOST", "localhost"),
        "port": int(credentials.get(f"RABBITMQ_{env_upper}_PORT") or os.environ.get(f"RABBITMQ_{env_upper}_PORT", "15672")),
        "username": credentials.get(f"RABBITMQ_{env_upper}_USERNAME") or os.environ.get(f"RABBITMQ_{env_upper}_USERNAME", "guest"),
        "password": credentials.get(f"RABBITMQ_{env_upper}_PASSWORD") or os.environ.get(f"RABBITMQ_{env_upper}_PASSWORD", "guest"),
        "vhost": credentials.get(f"RABBITMQ_{env_upper}_VHOST") or os.environ.get(f"RABBITMQ_{env_upper}_VHOST", "/"),
        "ssl": (credentials.get(f"RABBITMQ_{env_upper}_SSL") or os.environ.get(f"RABBITMQ_{env_upper}_SSL", "false")).lower() == "true",
    }

    return config


class RabbitMQClient:
    """RabbitMQ Management API client."""

    def __init__(self, config: dict):
        self.config = config
        protocol = "https" if config["ssl"] else "http"
        self.base_url = f"{protocol}://{config['host']}:{config['port']}/api"
        self.auth = HTTPBasicAuth(config["username"], config["password"])
        self.session = requests.Session()
        self.session.auth = self.auth

    def _request(self, endpoint: str) -> dict:
        """Make GET request to API endpoint."""
        url = f"{self.base_url}/{endpoint}"
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.ConnectionError as e:
            raise ConnectionError(f"Failed to connect to RabbitMQ at {self.config['host']}:{self.config['port']}: {e}")
        except requests.exceptions.HTTPError as e:
            if response.status_code == 401:
                raise PermissionError("Authentication failed - check username/password")
            raise RuntimeError(f"HTTP error: {e}")
        except requests.exceptions.Timeout:
            raise TimeoutError("Request timed out")
        except json.JSONDecodeError:
            raise RuntimeError("Invalid JSON response from server")

    def get_overview(self) -> dict:
        """Get server overview."""
        return self._request("overview")

    def get_nodes(self) -> list:
        """Get cluster nodes."""
        return self._request("nodes")

    def health_check(self) -> dict:
        """Perform health check."""
        try:
            # Use alarms endpoint for health check
            alarms = self._request("health/checks/alarms")
            return {"status": "ok", "alarms": alarms}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_queues(self, vhost: str = None) -> list:
        """Get all queues, optionally filtered by vhost."""
        if vhost:
            encoded_vhost = quote(vhost, safe='')
            return self._request(f"queues/{encoded_vhost}")
        return self._request("queues")

    def get_queue(self, name: str, vhost: str = "/") -> dict:
        """Get specific queue details."""
        encoded_vhost = quote(vhost, safe='')
        encoded_name = quote(name, safe='')
        return self._request(f"queues/{encoded_vhost}/{encoded_name}")

    def get_connections(self) -> list:
        """Get all connections."""
        return self._request("connections")

    def get_channels(self) -> list:
        """Get all channels."""
        return self._request("channels")

    def get_consumers(self) -> list:
        """Get all consumers."""
        return self._request("consumers")

    def get_exchanges(self, vhost: str = None) -> list:
        """Get all exchanges."""
        if vhost:
            encoded_vhost = quote(vhost, safe='')
            return self._request(f"exchanges/{encoded_vhost}")
        return self._request("exchanges")

    def get_bindings(self, queue_name: str, vhost: str = "/") -> list:
        """Get bindings for a queue."""
        encoded_vhost = quote(vhost, safe='')
        encoded_name = quote(queue_name, safe='')
        return self._request(f"queues/{encoded_vhost}/{encoded_name}/bindings")


def format_number(n) -> str:
    """Format number with thousands separator."""
    if n is None:
        return "0"
    return f"{n:,}"


def format_rate(rate_details: dict) -> str:
    """Format rate from rate_details dict."""
    if not rate_details:
        return "0/s"
    rate = rate_details.get("rate", 0)
    return f"{rate:.1f}/s"


def format_output(data, format_type: str) -> str:
    """Format output based on requested format."""
    if format_type == "json":
        return json.dumps(data, indent=2, default=str)
    else:
        if isinstance(data, dict):
            lines = []
            for k, v in data.items():
                if isinstance(v, dict):
                    lines.append(f"{k}:")
                    for k2, v2 in v.items():
                        lines.append(f"  {k2}: {v2}")
                else:
                    lines.append(f"{k}: {v}")
            return "\n".join(lines)
        elif isinstance(data, list):
            if not data:
                return "(empty)"
            return "\n".join(str(item) for item in data)
        else:
            return str(data) if data is not None else "(nil)"


def cmd_overview(client: RabbitMQClient, args) -> dict:
    """Get server overview."""
    overview = client.get_overview()

    result = {
        "RabbitMQ Version": overview.get("rabbitmq_version", "unknown"),
        "Erlang Version": overview.get("erlang_version", "unknown"),
        "Cluster Name": overview.get("cluster_name", "unknown"),
        "Node": overview.get("node", "unknown"),
    }

    # Message totals
    msg_stats = overview.get("queue_totals", {})
    result["Total Messages"] = format_number(msg_stats.get("messages", 0))
    result["Messages Ready"] = format_number(msg_stats.get("messages_ready", 0))
    result["Messages Unacked"] = format_number(msg_stats.get("messages_unacknowledged", 0))

    # Object totals
    obj_totals = overview.get("object_totals", {})
    result["Queues"] = format_number(obj_totals.get("queues", 0))
    result["Connections"] = format_number(obj_totals.get("connections", 0))
    result["Channels"] = format_number(obj_totals.get("channels", 0))
    result["Consumers"] = format_number(obj_totals.get("consumers", 0))
    result["Exchanges"] = format_number(obj_totals.get("exchanges", 0))

    return result


def cmd_nodes(client: RabbitMQClient, args) -> list:
    """Get cluster nodes."""
    nodes = client.get_nodes()

    result = []
    for node in nodes:
        node_info = {
            "name": node.get("name", "unknown"),
            "type": node.get("type", "unknown"),
            "running": "Yes" if node.get("running") else "No",
            "mem_used": f"{node.get('mem_used', 0) / (1024*1024*1024):.2f} GB",
            "mem_limit": f"{node.get('mem_limit', 0) / (1024*1024*1024):.2f} GB",
            "disk_free": f"{node.get('disk_free', 0) / (1024*1024*1024):.2f} GB",
            "fd_used": f"{node.get('fd_used', 0)}/{node.get('fd_total', 0)}",
            "sockets_used": f"{node.get('sockets_used', 0)}/{node.get('sockets_total', 0)}",
            "uptime": f"{node.get('uptime', 0) // 1000 // 60 // 60} hours",
        }
        result.append(node_info)

    return result


def cmd_health(client: RabbitMQClient, args) -> dict:
    """Get health check status."""
    health = client.health_check()

    if health.get("status") == "ok":
        alarms = health.get("alarms", {})
        if alarms.get("status") == "ok":
            return {"status": "HEALTHY", "message": "No alarms active"}
        else:
            return {"status": "WARNING", "alarms": alarms}
    else:
        return {"status": "ERROR", "message": health.get("message", "Unknown error")}


def cmd_queues(client: RabbitMQClient, args) -> list:
    """List all queues."""
    queues = client.get_queues(args.vhost)

    # Filter by name pattern if provided
    if hasattr(args, 'filter') and args.filter:
        queues = [q for q in queues if args.filter.lower() in q.get("name", "").lower()]

    # Filter to show only queues with backlog
    if hasattr(args, 'backlog') and args.backlog:
        queues = [q for q in queues if q.get("messages", 0) > 0]

    result = []
    for q in queues:
        queue_info = {
            "name": q.get("name", "unknown"),
            "messages": q.get("messages", 0),
            "ready": q.get("messages_ready", 0),
            "unacked": q.get("messages_unacknowledged", 0),
            "consumers": q.get("consumers", 0),
            "state": q.get("state", "unknown"),
            "vhost": q.get("vhost", "/"),
        }
        result.append(queue_info)

    # Sort by message count descending
    result.sort(key=lambda x: x["messages"], reverse=True)

    return result


def cmd_queue(client: RabbitMQClient, args) -> dict:
    """Get specific queue details."""
    vhost = args.vhost if hasattr(args, 'vhost') and args.vhost else "/"
    queue = client.get_queue(args.name, vhost)

    result = {
        "Name": queue.get("name", "unknown"),
        "VHost": queue.get("vhost", "/"),
        "State": queue.get("state", "unknown"),
        "Durable": "Yes" if queue.get("durable") else "No",
        "Auto-delete": "Yes" if queue.get("auto_delete") else "No",
        "Exclusive": "Yes" if queue.get("exclusive") else "No",
        "Messages": format_number(queue.get("messages", 0)),
        "Messages Ready": format_number(queue.get("messages_ready", 0)),
        "Messages Unacked": format_number(queue.get("messages_unacknowledged", 0)),
        "Consumers": queue.get("consumers", 0),
        "Memory": f"{queue.get('memory', 0) / 1024:.1f} KB",
    }

    # Add rate info if requested
    if hasattr(args, 'rates') and args.rates:
        msg_stats = queue.get("message_stats", {})
        result["Publish Rate"] = format_rate(msg_stats.get("publish_details"))
        result["Deliver Rate"] = format_rate(msg_stats.get("deliver_get_details"))
        result["Ack Rate"] = format_rate(msg_stats.get("ack_details"))
        result["Redeliver Rate"] = format_rate(msg_stats.get("redeliver_details"))

    # Add arguments if present
    arguments = queue.get("arguments", {})
    if arguments:
        result["Arguments"] = arguments

    return result


def cmd_connections(client: RabbitMQClient, args) -> list:
    """List connections."""
    connections = client.get_connections()

    result = []
    for conn in connections:
        conn_info = {
            "name": conn.get("name", "unknown")[:50],
            "user": conn.get("user", "unknown"),
            "state": conn.get("state", "unknown"),
            "channels": conn.get("channels", 0),
            "ssl": "Yes" if conn.get("ssl") else "No",
            "peer_host": conn.get("peer_host", "unknown"),
            "peer_port": conn.get("peer_port", 0),
        }
        result.append(conn_info)

    return result


def cmd_channels(client: RabbitMQClient, args) -> list:
    """List channels."""
    channels = client.get_channels()

    result = []
    for ch in channels:
        ch_info = {
            "name": ch.get("name", "unknown")[:50],
            "user": ch.get("user", "unknown"),
            "state": ch.get("state", "unknown"),
            "prefetch_count": ch.get("prefetch_count", 0),
            "consumer_count": ch.get("consumer_count", 0),
            "messages_unacked": ch.get("messages_unacknowledged", 0),
        }
        result.append(ch_info)

    return result


def cmd_consumers(client: RabbitMQClient, args) -> list:
    """List consumers."""
    consumers = client.get_consumers()

    result = []
    for c in consumers:
        consumer_info = {
            "queue": c.get("queue", {}).get("name", "unknown"),
            "consumer_tag": c.get("consumer_tag", "unknown")[:40],
            "channel": c.get("channel_details", {}).get("name", "unknown")[:30],
            "prefetch": c.get("prefetch_count", 0),
            "ack_required": "Yes" if c.get("ack_required") else "No",
            "exclusive": "Yes" if c.get("exclusive") else "No",
        }
        result.append(consumer_info)

    return result


def cmd_exchanges(client: RabbitMQClient, args) -> list:
    """List exchanges."""
    vhost = args.vhost if hasattr(args, 'vhost') and args.vhost else None
    exchanges = client.get_exchanges(vhost)

    result = []
    for ex in exchanges:
        # Skip default exchange
        name = ex.get("name", "")
        if not name:
            name = "(default)"

        ex_info = {
            "name": name,
            "type": ex.get("type", "unknown"),
            "durable": "Yes" if ex.get("durable") else "No",
            "auto_delete": "Yes" if ex.get("auto_delete") else "No",
            "internal": "Yes" if ex.get("internal") else "No",
            "vhost": ex.get("vhost", "/"),
        }
        result.append(ex_info)

    return result


def cmd_bindings(client: RabbitMQClient, args) -> list:
    """List bindings for a queue."""
    vhost = args.vhost if hasattr(args, 'vhost') and args.vhost else "/"
    bindings = client.get_bindings(args.name, vhost)

    result = []
    for b in bindings:
        binding_info = {
            "source": b.get("source", "(default)") or "(default)",
            "routing_key": b.get("routing_key", ""),
            "destination": b.get("destination", ""),
            "destination_type": b.get("destination_type", ""),
        }
        if b.get("arguments"):
            binding_info["arguments"] = b.get("arguments")
        result.append(binding_info)

    return result


def print_table(data: list, format_type: str):
    """Print data as a formatted table or JSON."""
    if format_type == "json":
        print(json.dumps(data, indent=2, default=str))
        return

    if not data:
        print("(no results)")
        return

    # Get column headers from first item
    headers = list(data[0].keys())

    # Calculate column widths
    widths = {}
    for h in headers:
        widths[h] = len(h)
        for row in data:
            val = str(row.get(h, ""))
            widths[h] = max(widths[h], len(val))

    # Print header
    header_line = "  ".join(h.upper().ljust(widths[h]) for h in headers)
    print(header_line)
    print("-" * len(header_line))

    # Print rows
    for row in data:
        row_line = "  ".join(str(row.get(h, "")).ljust(widths[h]) for h in headers)
        print(row_line)


def main():
    parser = argparse.ArgumentParser(
        description="Monitor RabbitMQ queues and health",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --env DEV overview
  %(prog)s --env DEV queues --backlog
  %(prog)s --env QA queue my-queue-name --rates
  %(prog)s --env PROD health
        """
    )

    # Global arguments
    parser.add_argument("--env", "-e", choices=ENVIRONMENTS,
                        help="Target environment: LOCAL, DEV, QA, UAT, PROD")
    parser.add_argument("--format", "-f", choices=["text", "json"], default="text",
                        help="Output format (default: text)")
    parser.add_argument("--output", "-o", help="Write output to file")
    parser.add_argument("--vhost", help="RabbitMQ vhost (default: from config)")
    parser.add_argument("--show-config", action="store_true",
                        help="Show connection configuration")

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Overview command
    subparsers.add_parser("overview", help="Get server overview")

    # Nodes command
    subparsers.add_parser("nodes", help="Get cluster nodes")

    # Health command
    subparsers.add_parser("health", help="Get health check status")

    # Queues command
    queues_parser = subparsers.add_parser("queues", help="List all queues")
    queues_parser.add_argument("--filter", help="Filter queues by name pattern")
    queues_parser.add_argument("--backlog", action="store_true",
                               help="Show only queues with messages > 0")

    # Queue command (single queue details)
    queue_parser = subparsers.add_parser("queue", help="Get specific queue details")
    queue_parser.add_argument("name", help="Queue name")
    queue_parser.add_argument("--rates", action="store_true",
                              help="Include message rates")

    # Connections command
    subparsers.add_parser("connections", help="List connections")

    # Channels command
    subparsers.add_parser("channels", help="List channels")

    # Consumers command
    subparsers.add_parser("consumers", help="List consumers")

    # Exchanges command
    subparsers.add_parser("exchanges", help="List exchanges")

    # Bindings command
    bindings_parser = subparsers.add_parser("bindings", help="List bindings for a queue")
    bindings_parser.add_argument("name", help="Queue name")

    args = parser.parse_args()

    # Load credentials
    credentials = load_credentials_from_file()

    # Prompt for environment if not provided
    if not args.env:
        print("Available environments: LOCAL, DEV, QA, UAT, PROD")
        args.env = input("Select environment: ").strip().upper()
        if args.env not in ENVIRONMENTS:
            print(f"Error: Invalid environment '{args.env}'")
            sys.exit(1)

    # Get environment config
    config = get_env_config(args.env, credentials)

    # Override vhost if provided via CLI
    if args.vhost:
        config["vhost"] = args.vhost

    # Show config if requested
    if args.show_config:
        print(f"\nRabbitMQ Configuration for {args.env}:")
        print(f"  Host: {config['host']}")
        print(f"  Port: {config['port']}")
        print(f"  Username: {config['username']}")
        print(f"  Password: {'****' if config['password'] else '(none)'}")
        print(f"  VHost: {config['vhost']}")
        print(f"  SSL: {config['ssl']}")
        sys.exit(0)

    # Require command
    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Command handlers
    commands = {
        "overview": cmd_overview,
        "nodes": cmd_nodes,
        "health": cmd_health,
        "queues": cmd_queues,
        "queue": cmd_queue,
        "connections": cmd_connections,
        "channels": cmd_channels,
        "consumers": cmd_consumers,
        "exchanges": cmd_exchanges,
        "bindings": cmd_bindings,
    }

    try:
        # Create client
        client = RabbitMQClient(config)

        # Execute command
        handler = commands.get(args.command)
        if not handler:
            print(f"Error: Unknown command '{args.command}'")
            sys.exit(1)

        result = handler(client, args)

        # Format and output
        if result is not None:
            if isinstance(result, list):
                if args.output:
                    output = json.dumps(result, indent=2, default=str) if args.format == "json" else format_output(result, args.format)
                    with open(args.output, "w") as f:
                        f.write(output)
                    print(f"Output written to {args.output}")
                else:
                    print_table(result, args.format)
            else:
                output = format_output(result, args.format)
                if args.output:
                    with open(args.output, "w") as f:
                        f.write(output)
                    print(f"Output written to {args.output}")
                else:
                    print(output)

    except ConnectionError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except PermissionError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except TimeoutError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except RuntimeError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nOperation cancelled.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
