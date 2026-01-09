#!/usr/bin/env python3
"""Amazon S3 access with multi-profile and region support.

Access S3 buckets and objects with:
- List buckets and objects
- Upload and download files
- Get object metadata
- Copy and delete operations
- Multiple AWS profiles
- Custom endpoints (VPC, LocalStack, MinIO)
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

# Venv auto-detection and re-exec
# If script is called with system Python instead of venv Python, re-exec with venv
_SKILL_DIR = Path(__file__).parent.parent
_VENV_DIR = _SKILL_DIR / ".venv"
_VENV_PYTHON = _VENV_DIR / "bin" / "python3"
_SETUP_SCRIPT = _SKILL_DIR / "setup.sh"

if not sys.prefix.startswith(str(_VENV_DIR)):
    if _VENV_PYTHON.exists():
        # Venv exists but script called with wrong Python - re-exec with venv Python
        os.execv(str(_VENV_PYTHON), [str(_VENV_PYTHON)] + sys.argv)
    else:
        # Venv doesn't exist - prompt to run setup
        print("Error: Virtual environment not found.")
        print(f"Run setup first: cd {_SKILL_DIR} && bash setup.sh")
        sys.exit(1)

try:
    import boto3
    from botocore.exceptions import ClientError, NoCredentialsError, ProfileNotFound
except ImportError:
    print("Error: boto3 library not installed")
    print("Install with: pip install boto3")
    sys.exit(1)

# Constants
SKILL_DIR = Path(__file__).parent.parent
CREDENTIALS_FILE = SKILL_DIR / "references" / ".credentials"

# Credential file search paths (in priority order)
CREDENTIAL_PATHS = [
    CREDENTIALS_FILE,
    Path.home() / ".claude" / "skills" / "s3-access" / ".credentials",
    Path(".credentials"),
]


def load_credentials() -> dict:
    """Load AWS credentials from .credentials file or environment."""
    creds = {
        "access_key": os.environ.get("AWS_ACCESS_KEY_ID"),
        "secret_key": os.environ.get("AWS_SECRET_ACCESS_KEY"),
        "region": os.environ.get("AWS_DEFAULT_REGION", "us-east-1"),
        "profile": os.environ.get("AWS_PROFILE"),
        "endpoint_url": os.environ.get("AWS_ENDPOINT_URL"),
        "session_token": os.environ.get("AWS_SESSION_TOKEN"),
    }

    # Try to load from credentials file if env vars not set
    if not creds["access_key"] and not creds["profile"]:
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

                        if key == "AWS_ACCESS_KEY_ID" and not creds["access_key"]:
                            creds["access_key"] = value
                        elif key == "AWS_SECRET_ACCESS_KEY" and not creds["secret_key"]:
                            creds["secret_key"] = value
                        elif key == "AWS_DEFAULT_REGION":
                            creds["region"] = value
                        elif key == "AWS_PROFILE":
                            creds["profile"] = value
                        elif key == "AWS_ENDPOINT_URL":
                            creds["endpoint_url"] = value
                        elif key == "AWS_SESSION_TOKEN":
                            creds["session_token"] = value

    return creds


def get_s3_client(creds: dict, profile: str = None, region: str = None, endpoint_url: str = None):
    """Create an S3 client with the given credentials."""
    # Override with explicit arguments
    if profile:
        creds["profile"] = profile
    if region:
        creds["region"] = region
    if endpoint_url:
        creds["endpoint_url"] = endpoint_url

    try:
        session_kwargs = {}
        if creds.get("profile"):
            session_kwargs["profile_name"] = creds["profile"]

        session = boto3.Session(**session_kwargs)

        client_kwargs = {"region_name": creds.get("region", "us-east-1")}

        # Use explicit credentials if provided (and no profile)
        if not creds.get("profile") and creds.get("access_key") and creds.get("secret_key"):
            client_kwargs["aws_access_key_id"] = creds["access_key"]
            client_kwargs["aws_secret_access_key"] = creds["secret_key"]
            if creds.get("session_token"):
                client_kwargs["aws_session_token"] = creds["session_token"]

        # Custom endpoint (VPC, LocalStack, MinIO)
        if creds.get("endpoint_url"):
            client_kwargs["endpoint_url"] = creds["endpoint_url"]

        return session.client("s3", **client_kwargs)

    except ProfileNotFound as e:
        print(f"Error: AWS profile not found: {creds.get('profile')}")
        print("Available profiles can be found in ~/.aws/credentials")
        sys.exit(1)
    except NoCredentialsError:
        print("Error: AWS credentials not found")
        print("\nTo set up credentials:")
        print("  1. Copy .credentials.example to .credentials")
        print("  2. Fill in your AWS access key and secret key")
        print("  3. Or run: /credential-setup s3-access")
        print("  4. Or configure AWS CLI: aws configure")
        sys.exit(1)


def parse_s3_path(path: str) -> tuple:
    """Parse an S3 path into bucket and key.

    Args:
        path: S3 path like 'bucket/key/path' or 's3://bucket/key/path'

    Returns:
        Tuple of (bucket, key) where key may be empty
    """
    # Remove s3:// prefix if present
    if path.startswith("s3://"):
        path = path[5:]

    # Split into bucket and key
    parts = path.split("/", 1)
    bucket = parts[0]
    key = parts[1] if len(parts) > 1 else ""

    return bucket, key


def format_size(size_bytes: int) -> str:
    """Format byte size to human readable string."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"


def format_date(dt) -> str:
    """Format datetime to readable string."""
    if dt is None:
        return "N/A"
    if hasattr(dt, "strftime"):
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    return str(dt)


def cmd_buckets(client, args):
    """List all S3 buckets."""
    try:
        response = client.list_buckets()
        buckets = response.get("Buckets", [])

        if not buckets:
            print("No buckets found")
            return

        print(f"\nS3 Buckets ({len(buckets)}):")
        print("-" * 60)

        for bucket in buckets:
            name = bucket["Name"]
            created = format_date(bucket.get("CreationDate"))
            print(f"  {name:<40} {created}")

        print()

    except ClientError as e:
        handle_error(e, "listing buckets")


def cmd_ls(client, args):
    """List objects in a bucket."""
    bucket, prefix = parse_s3_path(args.path)

    if not bucket:
        print("Error: Bucket name required")
        print("Usage: s3_access.py ls <bucket>[/prefix]")
        sys.exit(1)

    try:
        paginator = client.get_paginator("list_objects_v2")

        page_kwargs = {"Bucket": bucket}
        if prefix:
            page_kwargs["Prefix"] = prefix
        if not args.recursive and prefix:
            # Use delimiter for directory-like listing
            page_kwargs["Delimiter"] = "/"

        total_objects = 0
        total_size = 0
        shown = 0
        limit = args.limit or float("inf")

        print(f"\nContents of s3://{bucket}/{prefix}")
        print("-" * 70)

        for page in paginator.paginate(**page_kwargs):
            # Show common prefixes (directories)
            for prefix_info in page.get("CommonPrefixes", []):
                if shown >= limit:
                    break
                prefix_name = prefix_info["Prefix"]
                # Show relative to current prefix
                display_name = prefix_name[len(prefix):] if prefix else prefix_name
                print(f"  [DIR]  {display_name}")
                shown += 1

            # Show objects
            for obj in page.get("Contents", []):
                if shown >= limit:
                    break
                key = obj["Key"]
                size = obj.get("Size", 0)
                modified = format_date(obj.get("LastModified"))

                # Show relative to current prefix
                display_key = key[len(prefix):] if prefix else key

                # Skip if this is just the prefix itself (empty folder marker)
                if not display_key:
                    continue

                print(f"  {format_size(size):>10}  {modified}  {display_key}")
                total_objects += 1
                total_size += size
                shown += 1

        print("-" * 70)
        print(f"Total: {total_objects} objects, {format_size(total_size)}")
        if shown >= limit:
            print(f"(showing first {limit} results)")
        print()

    except ClientError as e:
        handle_error(e, f"listing s3://{bucket}/{prefix}")


def cmd_get(client, args):
    """Get object contents or download to file."""
    bucket, key = parse_s3_path(args.path)

    if not bucket or not key:
        print("Error: Bucket and key required")
        print("Usage: s3_access.py get <bucket/key>")
        sys.exit(1)

    try:
        # Get object
        response = client.get_object(Bucket=bucket, Key=key)

        content_length = response.get("ContentLength", 0)
        content_type = response.get("ContentType", "application/octet-stream")

        if args.output:
            # Download to file
            output_path = Path(args.output)
            with open(output_path, "wb") as f:
                for chunk in response["Body"].iter_chunks():
                    f.write(chunk)

            print(f"Downloaded: s3://{bucket}/{key}")
            print(f"  To: {output_path.absolute()}")
            print(f"  Size: {format_size(content_length)}")
            print(f"  Type: {content_type}")
        else:
            # Display contents
            body = response["Body"].read()

            # Check if it's text content
            is_text = content_type.startswith("text/") or content_type in [
                "application/json",
                "application/xml",
                "application/javascript",
                "application/x-yaml",
                "application/yaml",
            ]

            if is_text or content_length < 10000:
                try:
                    content = body.decode("utf-8")
                    print(content)
                except UnicodeDecodeError:
                    print(f"Binary file ({format_size(content_length)})")
                    print(f"Use --output to download: s3_access.py get {args.path} --output <file>")
            else:
                print(f"Large file ({format_size(content_length)})")
                print(f"Use --output to download: s3_access.py get {args.path} --output <file>")

    except ClientError as e:
        handle_error(e, f"getting s3://{bucket}/{key}")


def cmd_put(client, args):
    """Upload a file to S3."""
    local_path = Path(args.local)
    bucket, key = parse_s3_path(args.dest)

    if not bucket or not key:
        print("Error: Destination bucket and key required")
        print("Usage: s3_access.py put <local-file> <bucket/key>")
        sys.exit(1)

    if not local_path.exists():
        print(f"Error: Local file not found: {local_path}")
        sys.exit(1)

    try:
        file_size = local_path.stat().st_size

        # Determine content type
        import mimetypes
        content_type, _ = mimetypes.guess_type(str(local_path))
        if not content_type:
            content_type = "application/octet-stream"

        # Upload
        with open(local_path, "rb") as f:
            client.put_object(
                Bucket=bucket,
                Key=key,
                Body=f,
                ContentType=content_type,
            )

        print(f"Uploaded: {local_path}")
        print(f"  To: s3://{bucket}/{key}")
        print(f"  Size: {format_size(file_size)}")
        print(f"  Type: {content_type}")

    except ClientError as e:
        handle_error(e, f"uploading to s3://{bucket}/{key}")


def cmd_info(client, args):
    """Get object metadata."""
    bucket, key = parse_s3_path(args.path)

    if not bucket or not key:
        print("Error: Bucket and key required")
        print("Usage: s3_access.py info <bucket/key>")
        sys.exit(1)

    try:
        response = client.head_object(Bucket=bucket, Key=key)

        print(f"\nObject Info: s3://{bucket}/{key}")
        print("-" * 50)
        print(f"  Size:          {format_size(response.get('ContentLength', 0))}")
        print(f"  Content-Type:  {response.get('ContentType', 'N/A')}")
        print(f"  Last Modified: {format_date(response.get('LastModified'))}")
        print(f"  ETag:          {response.get('ETag', 'N/A')}")

        if response.get("StorageClass"):
            print(f"  Storage Class: {response.get('StorageClass')}")

        if response.get("ServerSideEncryption"):
            print(f"  Encryption:    {response.get('ServerSideEncryption')}")

        if response.get("VersionId"):
            print(f"  Version ID:    {response.get('VersionId')}")

        # Show metadata if present
        metadata = response.get("Metadata", {})
        if metadata:
            print(f"  Metadata:")
            for k, v in metadata.items():
                print(f"    {k}: {v}")

        print()

    except ClientError as e:
        handle_error(e, f"getting info for s3://{bucket}/{key}")


def cmd_rm(client, args):
    """Delete an object."""
    bucket, key = parse_s3_path(args.path)

    if not bucket or not key:
        print("Error: Bucket and key required")
        print("Usage: s3_access.py rm <bucket/key>")
        sys.exit(1)

    # Confirm deletion
    if not args.yes:
        confirm = input(f"Delete s3://{bucket}/{key}? [y/N] ")
        if confirm.lower() != "y":
            print("Cancelled")
            return

    try:
        client.delete_object(Bucket=bucket, Key=key)
        print(f"Deleted: s3://{bucket}/{key}")

    except ClientError as e:
        handle_error(e, f"deleting s3://{bucket}/{key}")


def cmd_cp(client, args):
    """Copy an object."""
    src_bucket, src_key = parse_s3_path(args.source)
    dest_bucket, dest_key = parse_s3_path(args.dest)

    if not src_bucket or not src_key:
        print("Error: Source bucket and key required")
        sys.exit(1)

    if not dest_bucket or not dest_key:
        print("Error: Destination bucket and key required")
        sys.exit(1)

    try:
        copy_source = {"Bucket": src_bucket, "Key": src_key}
        client.copy_object(
            CopySource=copy_source,
            Bucket=dest_bucket,
            Key=dest_key,
        )

        print(f"Copied: s3://{src_bucket}/{src_key}")
        print(f"    To: s3://{dest_bucket}/{dest_key}")

    except ClientError as e:
        handle_error(e, f"copying s3://{src_bucket}/{src_key}")


def handle_error(e, operation: str):
    """Handle AWS ClientError with helpful messages."""
    error_code = e.response.get("Error", {}).get("Code", "Unknown")
    error_message = e.response.get("Error", {}).get("Message", str(e))

    if error_code == "NoSuchBucket":
        print(f"Error: Bucket not found")
        print("Check that the bucket name is correct")
    elif error_code == "NoSuchKey":
        print(f"Error: Object not found")
        print("Check that the key path is correct")
    elif error_code == "AccessDenied":
        print(f"Error: Access denied")
        print("Check your IAM permissions for this bucket/object")
    elif error_code == "InvalidAccessKeyId":
        print(f"Error: Invalid AWS access key")
        print("Check your AWS_ACCESS_KEY_ID")
    elif error_code == "SignatureDoesNotMatch":
        print(f"Error: Invalid AWS secret key")
        print("Check your AWS_SECRET_ACCESS_KEY")
    elif error_code == "ExpiredToken":
        print(f"Error: AWS session token has expired")
        print("Refresh your credentials")
    elif error_code == "InvalidBucketName":
        print(f"Error: Invalid bucket name")
        print("Bucket names must be 3-63 characters, lowercase, and DNS-compliant")
    else:
        print(f"Error ({error_code}): {error_message}")

    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Access Amazon S3 buckets and objects.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s buckets
  %(prog)s ls my-bucket/path/
  %(prog)s get my-bucket/file.txt
  %(prog)s put local.txt my-bucket/remote.txt
  %(prog)s info my-bucket/file.txt
  %(prog)s rm my-bucket/file.txt
  %(prog)s cp my-bucket/src.txt my-bucket/dest.txt
        """,
    )

    # Common arguments
    parser.add_argument("--profile", "-p", help="AWS profile name")
    parser.add_argument("--region", "-r", help="AWS region")
    parser.add_argument("--endpoint-url", help="Custom S3 endpoint URL")

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Buckets command
    subparsers.add_parser("buckets", help="List all S3 buckets")

    # ls command
    ls_parser = subparsers.add_parser("ls", help="List objects in a bucket")
    ls_parser.add_argument("path", help="Bucket name or bucket/prefix")
    ls_parser.add_argument("--recursive", action="store_true", help="List all objects recursively")
    ls_parser.add_argument("--limit", "-l", type=int, help="Limit number of results")

    # get command
    get_parser = subparsers.add_parser("get", help="Get object contents or download")
    get_parser.add_argument("path", help="S3 path (bucket/key)")
    get_parser.add_argument("--output", "-o", help="Output file path")

    # put command
    put_parser = subparsers.add_parser("put", help="Upload a file to S3")
    put_parser.add_argument("local", help="Local file path")
    put_parser.add_argument("dest", help="S3 destination (bucket/key)")

    # info command
    info_parser = subparsers.add_parser("info", help="Get object metadata")
    info_parser.add_argument("path", help="S3 path (bucket/key)")

    # rm command
    rm_parser = subparsers.add_parser("rm", help="Delete an object")
    rm_parser.add_argument("path", help="S3 path (bucket/key)")
    rm_parser.add_argument("--yes", "-y", action="store_true", help="Skip confirmation")

    # cp command
    cp_parser = subparsers.add_parser("cp", help="Copy an object")
    cp_parser.add_argument("source", help="Source S3 path (bucket/key)")
    cp_parser.add_argument("dest", help="Destination S3 path (bucket/key)")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Load credentials and create client
    creds = load_credentials()
    client = get_s3_client(
        creds,
        profile=args.profile,
        region=args.region,
        endpoint_url=args.endpoint_url,
    )

    # Execute command
    if args.command == "buckets":
        cmd_buckets(client, args)
    elif args.command == "ls":
        cmd_ls(client, args)
    elif args.command == "get":
        cmd_get(client, args)
    elif args.command == "put":
        cmd_put(client, args)
    elif args.command == "info":
        cmd_info(client, args)
    elif args.command == "rm":
        cmd_rm(client, args)
    elif args.command == "cp":
        cmd_cp(client, args)


if __name__ == "__main__":
    main()
