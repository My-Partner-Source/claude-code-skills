#!/usr/bin/env python3
"""
Redis Access Script

Access Redis databases across DEV/QA/UAT/PROD environments with comprehensive
data type support and safety guardrails.

Usage:
    # String operations
    redis_access.py --env DEV get mykey
    redis_access.py --env DEV set mykey "value" --ttl 3600
    redis_access.py --env DEV del mykey

    # Key operations
    redis_access.py --env DEV keys "user:*"
    redis_access.py --env DEV type mykey
    redis_access.py --env DEV ttl mykey

    # Hash operations
    redis_access.py --env DEV hget myhash field
    redis_access.py --env DEV hset myhash field "value"
    redis_access.py --env DEV hgetall myhash

    # List operations
    redis_access.py --env DEV lrange mylist 0 -1
    redis_access.py --env DEV lpush mylist "value"

    # Set operations
    redis_access.py --env DEV smembers myset
    redis_access.py --env DEV sadd myset "member"

    # Sorted set operations
    redis_access.py --env DEV zrange myzset 0 -1
    redis_access.py --env DEV zadd myzset 1.0 "member"

    # Server info
    redis_access.py --env DEV info
    redis_access.py --env DEV dbsize
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

# Auto-reexec with venv if needed
SCRIPT_DIR = Path(__file__).resolve().parent.parent
VENV_PYTHON = SCRIPT_DIR / ".venv" / "bin" / "python3"

if VENV_PYTHON.exists() and sys.executable != str(VENV_PYTHON):
    os.execv(str(VENV_PYTHON), [str(VENV_PYTHON), __file__] + sys.argv[1:])

try:
    import redis
except ImportError:
    print("Error: redis package not installed.")
    print("Run setup first: cd ~/.claude/skills/redis-access && bash setup.sh")
    sys.exit(1)

# Valid environments
ENVIRONMENTS = ["DEV", "QA", "UAT", "PROD"]

# Write operations that require confirmation
WRITE_OPERATIONS = {
    "set", "del", "hset", "hdel", "lpush", "rpush", "lpop", "rpop",
    "sadd", "srem", "zadd", "zrem", "expire", "flushdb", "flushall"
}


def load_credentials_from_file() -> dict:
    """Load credentials from .credentials file."""
    credentials = {}

    # Search locations for .credentials file
    search_paths = [
        SCRIPT_DIR / "references" / ".credentials",
        Path.cwd() / "references" / ".credentials",
        Path.cwd() / ".credentials",
        Path.home() / ".claude" / "skills" / "redis-access" / "references" / ".credentials",
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
        "host": credentials.get(f"REDIS_{env_upper}_HOST") or os.environ.get(f"REDIS_{env_upper}_HOST", "localhost"),
        "port": int(credentials.get(f"REDIS_{env_upper}_PORT") or os.environ.get(f"REDIS_{env_upper}_PORT", "6379")),
        "password": credentials.get(f"REDIS_{env_upper}_PASSWORD") or os.environ.get(f"REDIS_{env_upper}_PASSWORD", ""),
        "db": int(credentials.get(f"REDIS_{env_upper}_DB") or os.environ.get(f"REDIS_{env_upper}_DB", "0")),
        "ssl": (credentials.get(f"REDIS_{env_upper}_SSL") or os.environ.get(f"REDIS_{env_upper}_SSL", "false")).lower() == "true",
    }

    return config


def create_redis_client(config: dict) -> redis.Redis:
    """Create Redis client from config."""
    kwargs = {
        "host": config["host"],
        "port": config["port"],
        "db": config["db"],
        "decode_responses": True,
    }

    if config["password"]:
        kwargs["password"] = config["password"]

    if config["ssl"]:
        kwargs["ssl"] = True

    return redis.Redis(**kwargs)


def confirm_write(env: str, operation: str, key: str, dry_run: bool, yes: bool) -> bool:
    """Confirm write operation, with special handling for PROD."""
    if dry_run:
        print(f"[DRY RUN] Would execute: {operation} on key '{key}'")
        return False

    if yes:
        return True

    if env.upper() == "PROD":
        print(f"\n*** WARNING: You are about to perform a WRITE operation on PROD ***")
        print(f"Operation: {operation}")
        print(f"Key: {key}")
        confirm = input("Type 'PROD' to confirm: ")
        if confirm != "PROD":
            print("Operation cancelled.")
            return False
    else:
        print(f"\nWrite operation: {operation} on key '{key}' in {env}")
        confirm = input("Confirm? (y/N): ")
        if confirm.lower() != "y":
            print("Operation cancelled.")
            return False

    return True


def format_output(data, format_type: str) -> str:
    """Format output based on requested format."""
    if format_type == "json":
        return json.dumps(data, indent=2, default=str)
    else:
        if isinstance(data, dict):
            lines = []
            for k, v in data.items():
                lines.append(f"{k}: {v}")
            return "\n".join(lines)
        elif isinstance(data, (list, set)):
            return "\n".join(str(item) for item in data)
        else:
            return str(data) if data is not None else "(nil)"


def cmd_get(client, args):
    """GET command - get string value."""
    value = client.get(args.key)
    return value


def cmd_set(client, args):
    """SET command - set string value."""
    if not confirm_write(args.env, "SET", args.key, args.dry_run, args.yes):
        return None

    kwargs = {}
    if args.ttl:
        kwargs["ex"] = args.ttl

    result = client.set(args.key, args.value, **kwargs)
    return "OK" if result else "FAILED"


def cmd_del(client, args):
    """DEL command - delete key."""
    if not confirm_write(args.env, "DEL", args.key, args.dry_run, args.yes):
        return None

    result = client.delete(args.key)
    return f"Deleted {result} key(s)"


def cmd_keys(client, args):
    """KEYS command - list keys matching pattern."""
    keys = client.keys(args.pattern)
    return sorted(keys)


def cmd_type(client, args):
    """TYPE command - get key type."""
    return client.type(args.key)


def cmd_ttl(client, args):
    """TTL command - get time to live."""
    ttl = client.ttl(args.key)
    if ttl == -2:
        return "Key does not exist"
    elif ttl == -1:
        return "Key has no expiration"
    else:
        return f"{ttl} seconds"


def cmd_exists(client, args):
    """EXISTS command - check if key exists."""
    exists = client.exists(args.key)
    return "Yes" if exists else "No"


def cmd_expire(client, args):
    """EXPIRE command - set key expiration."""
    if not confirm_write(args.env, "EXPIRE", args.key, args.dry_run, args.yes):
        return None

    result = client.expire(args.key, args.seconds)
    return "OK" if result else "Key does not exist"


def cmd_hget(client, args):
    """HGET command - get hash field."""
    return client.hget(args.key, args.field)


def cmd_hset(client, args):
    """HSET command - set hash field."""
    if not confirm_write(args.env, "HSET", args.key, args.dry_run, args.yes):
        return None

    result = client.hset(args.key, args.field, args.value)
    return f"Fields added: {result}"


def cmd_hgetall(client, args):
    """HGETALL command - get all hash fields."""
    return client.hgetall(args.key)


def cmd_hdel(client, args):
    """HDEL command - delete hash field."""
    if not confirm_write(args.env, "HDEL", args.key, args.dry_run, args.yes):
        return None

    result = client.hdel(args.key, args.field)
    return f"Deleted {result} field(s)"


def cmd_hkeys(client, args):
    """HKEYS command - get all hash field names."""
    return client.hkeys(args.key)


def cmd_hlen(client, args):
    """HLEN command - get hash length."""
    return client.hlen(args.key)


def cmd_lrange(client, args):
    """LRANGE command - get list range."""
    return client.lrange(args.key, args.start, args.stop)


def cmd_lpush(client, args):
    """LPUSH command - push to list head."""
    if not confirm_write(args.env, "LPUSH", args.key, args.dry_run, args.yes):
        return None

    result = client.lpush(args.key, args.value)
    return f"List length: {result}"


def cmd_rpush(client, args):
    """RPUSH command - push to list tail."""
    if not confirm_write(args.env, "RPUSH", args.key, args.dry_run, args.yes):
        return None

    result = client.rpush(args.key, args.value)
    return f"List length: {result}"


def cmd_llen(client, args):
    """LLEN command - get list length."""
    return client.llen(args.key)


def cmd_lpop(client, args):
    """LPOP command - pop from list head."""
    if not confirm_write(args.env, "LPOP", args.key, args.dry_run, args.yes):
        return None

    return client.lpop(args.key)


def cmd_rpop(client, args):
    """RPOP command - pop from list tail."""
    if not confirm_write(args.env, "RPOP", args.key, args.dry_run, args.yes):
        return None

    return client.rpop(args.key)


def cmd_smembers(client, args):
    """SMEMBERS command - get set members."""
    return list(client.smembers(args.key))


def cmd_sadd(client, args):
    """SADD command - add to set."""
    if not confirm_write(args.env, "SADD", args.key, args.dry_run, args.yes):
        return None

    result = client.sadd(args.key, args.member)
    return f"Members added: {result}"


def cmd_srem(client, args):
    """SREM command - remove from set."""
    if not confirm_write(args.env, "SREM", args.key, args.dry_run, args.yes):
        return None

    result = client.srem(args.key, args.member)
    return f"Members removed: {result}"


def cmd_sismember(client, args):
    """SISMEMBER command - check set membership."""
    result = client.sismember(args.key, args.member)
    return "Yes" if result else "No"


def cmd_scard(client, args):
    """SCARD command - get set cardinality."""
    return client.scard(args.key)


def cmd_zrange(client, args):
    """ZRANGE command - get sorted set range."""
    if args.withscores:
        result = client.zrange(args.key, args.start, args.stop, withscores=True)
        return [{"member": m, "score": s} for m, s in result]
    return client.zrange(args.key, args.start, args.stop)


def cmd_zadd(client, args):
    """ZADD command - add to sorted set."""
    if not confirm_write(args.env, "ZADD", args.key, args.dry_run, args.yes):
        return None

    result = client.zadd(args.key, {args.member: args.score})
    return f"Members added: {result}"


def cmd_zscore(client, args):
    """ZSCORE command - get member score."""
    return client.zscore(args.key, args.member)


def cmd_zrem(client, args):
    """ZREM command - remove from sorted set."""
    if not confirm_write(args.env, "ZREM", args.key, args.dry_run, args.yes):
        return None

    result = client.zrem(args.key, args.member)
    return f"Members removed: {result}"


def cmd_zcard(client, args):
    """ZCARD command - get sorted set cardinality."""
    return client.zcard(args.key)


def cmd_info(client, args):
    """INFO command - get server info."""
    if args.section:
        info = client.info(args.section)
    else:
        info = client.info()
    return info


def cmd_dbsize(client, args):
    """DBSIZE command - get number of keys."""
    return client.dbsize()


def cmd_ping(client, args):
    """PING command - test connection."""
    return client.ping()


def cmd_flushdb(client, args):
    """FLUSHDB command - delete all keys in current database."""
    if not confirm_write(args.env, "FLUSHDB", f"ALL KEYS in DB {args.db or 'current'}", args.dry_run, args.yes):
        return None

    client.flushdb()
    return "OK"


def main():
    parser = argparse.ArgumentParser(
        description="Access Redis databases with multi-environment support",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --env DEV get mykey
  %(prog)s --env DEV set mykey "value" --ttl 3600
  %(prog)s --env QA hgetall session:user:123
  %(prog)s --env UAT keys "cache:*"
  %(prog)s --env PROD info --section memory
        """
    )

    # Global arguments
    parser.add_argument("--env", "-e", choices=ENVIRONMENTS,
                        help="Target environment: DEV, QA, UAT, PROD")
    parser.add_argument("--format", "-f", choices=["text", "json"], default="text",
                        help="Output format (default: text)")
    parser.add_argument("--output", "-o", help="Write output to file")
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview write operations without executing")
    parser.add_argument("--yes", "-y", action="store_true",
                        help="Skip confirmation prompts")
    parser.add_argument("--show-config", action="store_true",
                        help="Show connection configuration")

    subparsers = parser.add_subparsers(dest="command", help="Redis commands")

    # String commands
    get_parser = subparsers.add_parser("get", help="Get string value")
    get_parser.add_argument("key", help="Key name")

    set_parser = subparsers.add_parser("set", help="Set string value")
    set_parser.add_argument("key", help="Key name")
    set_parser.add_argument("value", help="Value to set")
    set_parser.add_argument("--ttl", type=int, help="Time to live in seconds")

    del_parser = subparsers.add_parser("del", help="Delete key")
    del_parser.add_argument("key", help="Key name")

    # Key commands
    keys_parser = subparsers.add_parser("keys", help="List keys matching pattern")
    keys_parser.add_argument("pattern", help="Key pattern (e.g., 'user:*')")

    type_parser = subparsers.add_parser("type", help="Get key type")
    type_parser.add_argument("key", help="Key name")

    ttl_parser = subparsers.add_parser("ttl", help="Get key TTL")
    ttl_parser.add_argument("key", help="Key name")

    exists_parser = subparsers.add_parser("exists", help="Check if key exists")
    exists_parser.add_argument("key", help="Key name")

    expire_parser = subparsers.add_parser("expire", help="Set key expiration")
    expire_parser.add_argument("key", help="Key name")
    expire_parser.add_argument("seconds", type=int, help="TTL in seconds")

    # Hash commands
    hget_parser = subparsers.add_parser("hget", help="Get hash field")
    hget_parser.add_argument("key", help="Hash key")
    hget_parser.add_argument("field", help="Field name")

    hset_parser = subparsers.add_parser("hset", help="Set hash field")
    hset_parser.add_argument("key", help="Hash key")
    hset_parser.add_argument("field", help="Field name")
    hset_parser.add_argument("value", help="Field value")

    hgetall_parser = subparsers.add_parser("hgetall", help="Get all hash fields")
    hgetall_parser.add_argument("key", help="Hash key")

    hdel_parser = subparsers.add_parser("hdel", help="Delete hash field")
    hdel_parser.add_argument("key", help="Hash key")
    hdel_parser.add_argument("field", help="Field name")

    hkeys_parser = subparsers.add_parser("hkeys", help="Get hash field names")
    hkeys_parser.add_argument("key", help="Hash key")

    hlen_parser = subparsers.add_parser("hlen", help="Get hash length")
    hlen_parser.add_argument("key", help="Hash key")

    # List commands
    lrange_parser = subparsers.add_parser("lrange", help="Get list range")
    lrange_parser.add_argument("key", help="List key")
    lrange_parser.add_argument("start", type=int, help="Start index")
    lrange_parser.add_argument("stop", type=int, help="Stop index")

    lpush_parser = subparsers.add_parser("lpush", help="Push to list head")
    lpush_parser.add_argument("key", help="List key")
    lpush_parser.add_argument("value", help="Value to push")

    rpush_parser = subparsers.add_parser("rpush", help="Push to list tail")
    rpush_parser.add_argument("key", help="List key")
    rpush_parser.add_argument("value", help="Value to push")

    llen_parser = subparsers.add_parser("llen", help="Get list length")
    llen_parser.add_argument("key", help="List key")

    lpop_parser = subparsers.add_parser("lpop", help="Pop from list head")
    lpop_parser.add_argument("key", help="List key")

    rpop_parser = subparsers.add_parser("rpop", help="Pop from list tail")
    rpop_parser.add_argument("key", help="List key")

    # Set commands
    smembers_parser = subparsers.add_parser("smembers", help="Get set members")
    smembers_parser.add_argument("key", help="Set key")

    sadd_parser = subparsers.add_parser("sadd", help="Add to set")
    sadd_parser.add_argument("key", help="Set key")
    sadd_parser.add_argument("member", help="Member to add")

    srem_parser = subparsers.add_parser("srem", help="Remove from set")
    srem_parser.add_argument("key", help="Set key")
    srem_parser.add_argument("member", help="Member to remove")

    sismember_parser = subparsers.add_parser("sismember", help="Check set membership")
    sismember_parser.add_argument("key", help="Set key")
    sismember_parser.add_argument("member", help="Member to check")

    scard_parser = subparsers.add_parser("scard", help="Get set cardinality")
    scard_parser.add_argument("key", help="Set key")

    # Sorted set commands
    zrange_parser = subparsers.add_parser("zrange", help="Get sorted set range")
    zrange_parser.add_argument("key", help="Sorted set key")
    zrange_parser.add_argument("start", type=int, help="Start index")
    zrange_parser.add_argument("stop", type=int, help="Stop index")
    zrange_parser.add_argument("--withscores", action="store_true", help="Include scores")

    zadd_parser = subparsers.add_parser("zadd", help="Add to sorted set")
    zadd_parser.add_argument("key", help="Sorted set key")
    zadd_parser.add_argument("score", type=float, help="Score")
    zadd_parser.add_argument("member", help="Member")

    zscore_parser = subparsers.add_parser("zscore", help="Get member score")
    zscore_parser.add_argument("key", help="Sorted set key")
    zscore_parser.add_argument("member", help="Member")

    zrem_parser = subparsers.add_parser("zrem", help="Remove from sorted set")
    zrem_parser.add_argument("key", help="Sorted set key")
    zrem_parser.add_argument("member", help="Member to remove")

    zcard_parser = subparsers.add_parser("zcard", help="Get sorted set cardinality")
    zcard_parser.add_argument("key", help="Sorted set key")

    # Server commands
    info_parser = subparsers.add_parser("info", help="Get server info")
    info_parser.add_argument("--section", help="Info section (server, memory, etc.)")

    dbsize_parser = subparsers.add_parser("dbsize", help="Get number of keys")

    ping_parser = subparsers.add_parser("ping", help="Test connection")

    flushdb_parser = subparsers.add_parser("flushdb", help="Delete all keys in database")
    flushdb_parser.add_argument("--db", type=int, help="Database number")

    args = parser.parse_args()

    # Load credentials
    credentials = load_credentials_from_file()

    # Prompt for environment if not provided
    if not args.env:
        print("Available environments: DEV, QA, UAT, PROD")
        args.env = input("Select environment: ").strip().upper()
        if args.env not in ENVIRONMENTS:
            print(f"Error: Invalid environment '{args.env}'")
            sys.exit(1)

    # Get environment config
    config = get_env_config(args.env, credentials)

    # Show config if requested
    if args.show_config:
        print(f"\nRedis Configuration for {args.env}:")
        print(f"  Host: {config['host']}")
        print(f"  Port: {config['port']}")
        print(f"  Database: {config['db']}")
        print(f"  SSL: {config['ssl']}")
        print(f"  Password: {'****' if config['password'] else '(none)'}")
        sys.exit(0)

    # Require command
    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Command handlers
    commands = {
        "get": cmd_get,
        "set": cmd_set,
        "del": cmd_del,
        "keys": cmd_keys,
        "type": cmd_type,
        "ttl": cmd_ttl,
        "exists": cmd_exists,
        "expire": cmd_expire,
        "hget": cmd_hget,
        "hset": cmd_hset,
        "hgetall": cmd_hgetall,
        "hdel": cmd_hdel,
        "hkeys": cmd_hkeys,
        "hlen": cmd_hlen,
        "lrange": cmd_lrange,
        "lpush": cmd_lpush,
        "rpush": cmd_rpush,
        "llen": cmd_llen,
        "lpop": cmd_lpop,
        "rpop": cmd_rpop,
        "smembers": cmd_smembers,
        "sadd": cmd_sadd,
        "srem": cmd_srem,
        "sismember": cmd_sismember,
        "scard": cmd_scard,
        "zrange": cmd_zrange,
        "zadd": cmd_zadd,
        "zscore": cmd_zscore,
        "zrem": cmd_zrem,
        "zcard": cmd_zcard,
        "info": cmd_info,
        "dbsize": cmd_dbsize,
        "ping": cmd_ping,
        "flushdb": cmd_flushdb,
    }

    try:
        # Create client
        client = create_redis_client(config)

        # Test connection
        client.ping()

        # Execute command
        handler = commands.get(args.command)
        if not handler:
            print(f"Error: Unknown command '{args.command}'")
            sys.exit(1)

        result = handler(client, args)

        if result is not None:
            output = format_output(result, args.format)

            if args.output:
                with open(args.output, "w") as f:
                    f.write(output)
                print(f"Output written to {args.output}")
            else:
                print(output)

    except redis.ConnectionError as e:
        print(f"Error: Failed to connect to Redis at {config['host']}:{config['port']}")
        print(f"Details: {e}")
        sys.exit(1)
    except redis.AuthenticationError as e:
        print(f"Error: Authentication failed")
        print(f"Details: {e}")
        sys.exit(1)
    except redis.RedisError as e:
        print(f"Error: Redis operation failed")
        print(f"Details: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nOperation cancelled.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
