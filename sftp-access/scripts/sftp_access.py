#!/usr/bin/env python3
"""SFTP access with password and SSH key authentication support.

Access remote SFTP servers with:
- List directories
- Upload and download files
- Get file metadata
- Delete files and directories
- Create directories
- Password and SSH key authentication
"""

import argparse
import os
import re
import stat
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
    import paramiko
    from paramiko.ssh_exception import (
        AuthenticationException,
        SSHException,
        NoValidConnectionsError,
    )
except ImportError:
    print("Error: paramiko library not installed")
    print("Install with: pip install paramiko")
    sys.exit(1)

# Constants
SKILL_DIR = Path(__file__).parent.parent
CREDENTIALS_FILE = SKILL_DIR / "references" / ".credentials"

# Credential file search paths (in priority order)
CREDENTIAL_PATHS = [
    CREDENTIALS_FILE,
    Path.home() / ".claude" / "skills" / "sftp-access" / ".credentials",
    Path(".credentials"),
]


def load_credentials() -> dict:
    """Load SFTP credentials from .credentials file or environment."""
    creds = {
        "host": os.environ.get("SFTP_HOST"),
        "port": int(os.environ.get("SFTP_PORT", "22")),
        "username": os.environ.get("SFTP_USERNAME"),
        "password": os.environ.get("SFTP_PASSWORD"),
        "key_file": os.environ.get("SFTP_KEY_FILE"),
        "key_passphrase": os.environ.get("SFTP_KEY_PASSPHRASE"),
    }

    # Try to load from credentials file if env vars not set
    if not creds["host"]:
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

                        if key == "SFTP_HOST" and not creds["host"]:
                            creds["host"] = value
                        elif key == "SFTP_PORT":
                            creds["port"] = int(value) if value else 22
                        elif key == "SFTP_USERNAME" and not creds["username"]:
                            creds["username"] = value
                        elif key == "SFTP_PASSWORD" and not creds["password"]:
                            creds["password"] = value
                        elif key == "SFTP_KEY_FILE" and not creds["key_file"]:
                            creds["key_file"] = value
                        elif key == "SFTP_KEY_PASSPHRASE" and not creds["key_passphrase"]:
                            creds["key_passphrase"] = value

    return creds


def get_sftp_client(creds: dict, host: str = None, port: int = None,
                    user: str = None, password: str = None,
                    key_file: str = None, timeout: int = 30):
    """Create an SFTP client connection.

    Returns:
        Tuple of (Transport, SFTPClient) - caller must close both
    """
    # Override with explicit arguments
    if host:
        creds["host"] = host
    if port:
        creds["port"] = port
    if user:
        creds["username"] = user
    if password:
        creds["password"] = password
    if key_file:
        creds["key_file"] = key_file

    # Validate required credentials
    if not creds.get("host"):
        print("Error: SFTP host not specified")
        print("\nTo set up credentials:")
        print("  1. Copy .credentials.example to .credentials")
        print("  2. Fill in your SFTP host and authentication details")
        print("  3. Or run: /credential-setup sftp-access")
        print("  4. Or use --host argument")
        sys.exit(1)

    if not creds.get("username"):
        print("Error: SFTP username not specified")
        print("Use --user argument or set SFTP_USERNAME in .credentials")
        sys.exit(1)

    if not creds.get("password") and not creds.get("key_file"):
        print("Error: No authentication method specified")
        print("Provide either --password or --key argument")
        print("Or set SFTP_PASSWORD or SFTP_KEY_FILE in .credentials")
        sys.exit(1)

    try:
        # Create transport
        transport = paramiko.Transport((creds["host"], creds.get("port", 22)))
        transport.connect(timeout=timeout)

        # Authenticate
        if creds.get("key_file"):
            # SSH key authentication
            key_path = Path(creds["key_file"]).expanduser()
            if not key_path.exists():
                print(f"Error: SSH key file not found: {key_path}")
                sys.exit(1)

            try:
                # Try loading as different key types
                passphrase = creds.get("key_passphrase")
                key = None

                for key_class in [paramiko.Ed25519Key, paramiko.RSAKey,
                                  paramiko.ECDSAKey, paramiko.DSSKey]:
                    try:
                        key = key_class.from_private_key_file(
                            str(key_path),
                            password=passphrase
                        )
                        break
                    except (paramiko.SSHException, ValueError):
                        continue

                if key is None:
                    print(f"Error: Could not load SSH key: {key_path}")
                    print("Supported formats: Ed25519, RSA, ECDSA, DSS")
                    sys.exit(1)

                transport.auth_publickey(creds["username"], key)

            except paramiko.PasswordRequiredException:
                print("Error: SSH key is encrypted but no passphrase provided")
                print("Set SFTP_KEY_PASSPHRASE in .credentials")
                sys.exit(1)
        else:
            # Password authentication
            transport.auth_password(creds["username"], creds["password"])

        # Create SFTP client
        sftp = paramiko.SFTPClient.from_transport(transport)
        return transport, sftp

    except AuthenticationException:
        print("Error: Authentication failed")
        print("Check your username and password/SSH key")
        sys.exit(1)
    except NoValidConnectionsError:
        print(f"Error: Could not connect to {creds['host']}:{creds.get('port', 22)}")
        print("Check the hostname and port, and ensure the server is reachable")
        sys.exit(1)
    except SSHException as e:
        print(f"Error: SSH error: {e}")
        sys.exit(1)
    except TimeoutError:
        print(f"Error: Connection timed out")
        print(f"Server: {creds['host']}:{creds.get('port', 22)}")
        print("Check network connectivity or increase timeout with --timeout")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


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


def format_date(timestamp: int) -> str:
    """Format Unix timestamp to readable string."""
    if timestamp is None:
        return "N/A"
    try:
        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except (ValueError, OSError):
        return "N/A"


def format_permissions(mode: int) -> str:
    """Format file mode to ls-style permission string."""
    # File type
    if stat.S_ISDIR(mode):
        result = "d"
    elif stat.S_ISLNK(mode):
        result = "l"
    else:
        result = "-"

    # Owner permissions
    result += "r" if mode & stat.S_IRUSR else "-"
    result += "w" if mode & stat.S_IWUSR else "-"
    result += "x" if mode & stat.S_IXUSR else "-"

    # Group permissions
    result += "r" if mode & stat.S_IRGRP else "-"
    result += "w" if mode & stat.S_IWGRP else "-"
    result += "x" if mode & stat.S_IXGRP else "-"

    # Other permissions
    result += "r" if mode & stat.S_IROTH else "-"
    result += "w" if mode & stat.S_IWOTH else "-"
    result += "x" if mode & stat.S_IXOTH else "-"

    return result


def cmd_ls(sftp, args):
    """List remote directory contents."""
    remote_path = args.path or "."

    try:
        # Get directory listing with attributes
        entries = sftp.listdir_attr(remote_path)

        if not entries:
            print(f"Empty directory: {remote_path}")
            return

        print(f"\nContents of {remote_path}")
        print("-" * 70)

        total_size = 0
        file_count = 0
        dir_count = 0

        # Sort: directories first, then alphabetically
        entries.sort(key=lambda x: (not stat.S_ISDIR(x.st_mode), x.filename.lower()))

        for entry in entries:
            perms = format_permissions(entry.st_mode)
            size = entry.st_size
            modified = format_date(entry.st_mtime)
            name = entry.filename

            if stat.S_ISDIR(entry.st_mode):
                print(f"  {perms}  {'<DIR>':>10}  {modified}  {name}/")
                dir_count += 1
            else:
                print(f"  {perms}  {format_size(size):>10}  {modified}  {name}")
                total_size += size
                file_count += 1

        print("-" * 70)
        print(f"Total: {file_count} files ({format_size(total_size)}), {dir_count} directories")
        print()

    except IOError as e:
        if "No such file" in str(e) or e.errno == 2:
            print(f"Error: Path not found: {remote_path}")
        elif "Permission denied" in str(e) or e.errno == 13:
            print(f"Error: Permission denied: {remote_path}")
        else:
            print(f"Error listing directory: {e}")
        sys.exit(1)


def cmd_get(sftp, args):
    """Get file contents or download to local file."""
    remote_path = args.path

    try:
        # Check if it's a file
        file_stat = sftp.stat(remote_path)
        if stat.S_ISDIR(file_stat.st_mode):
            print(f"Error: {remote_path} is a directory")
            print("Use 'ls' to list directory contents")
            sys.exit(1)

        file_size = file_stat.st_size

        if args.output:
            # Download to local file
            output_path = Path(args.output)
            sftp.get(remote_path, str(output_path))

            print(f"Downloaded: {remote_path}")
            print(f"  To: {output_path.absolute()}")
            print(f"  Size: {format_size(file_size)}")
        else:
            # Display contents
            with sftp.open(remote_path, "r") as f:
                # Check if file is too large for display
                if file_size > 100000:
                    print(f"Large file ({format_size(file_size)})")
                    print(f"Use --output to download: sftp_access.py get {remote_path} --output <file>")
                    return

                try:
                    content = f.read()
                    if isinstance(content, bytes):
                        content = content.decode("utf-8")
                    print(content)
                except UnicodeDecodeError:
                    print(f"Binary file ({format_size(file_size)})")
                    print(f"Use --output to download: sftp_access.py get {remote_path} --output <file>")

    except IOError as e:
        if "No such file" in str(e) or e.errno == 2:
            print(f"Error: File not found: {remote_path}")
        elif "Permission denied" in str(e) or e.errno == 13:
            print(f"Error: Permission denied: {remote_path}")
        else:
            print(f"Error getting file: {e}")
        sys.exit(1)


def cmd_put(sftp, args):
    """Upload a local file to SFTP server."""
    local_path = Path(args.local)
    remote_path = args.dest

    if not local_path.exists():
        print(f"Error: Local file not found: {local_path}")
        sys.exit(1)

    if not local_path.is_file():
        print(f"Error: {local_path} is not a file")
        sys.exit(1)

    try:
        file_size = local_path.stat().st_size

        # Upload file
        sftp.put(str(local_path), remote_path)

        print(f"Uploaded: {local_path}")
        print(f"  To: {remote_path}")
        print(f"  Size: {format_size(file_size)}")

    except IOError as e:
        if "No such file" in str(e) or e.errno == 2:
            print(f"Error: Remote path not found: {remote_path}")
            print("Check that the parent directory exists")
        elif "Permission denied" in str(e) or e.errno == 13:
            print(f"Error: Permission denied: {remote_path}")
        else:
            print(f"Error uploading file: {e}")
        sys.exit(1)


def cmd_info(sftp, args):
    """Get file/directory metadata."""
    remote_path = args.path

    try:
        file_stat = sftp.stat(remote_path)

        print(f"\nFile Info: {remote_path}")
        print("-" * 50)

        # File type
        if stat.S_ISDIR(file_stat.st_mode):
            print(f"  Type:          Directory")
        elif stat.S_ISLNK(file_stat.st_mode):
            print(f"  Type:          Symbolic Link")
        else:
            print(f"  Type:          File")

        print(f"  Size:          {format_size(file_stat.st_size)}")
        print(f"  Permissions:   {format_permissions(file_stat.st_mode)} ({oct(file_stat.st_mode)[-3:]})")
        print(f"  Owner UID:     {file_stat.st_uid}")
        print(f"  Group GID:     {file_stat.st_gid}")
        print(f"  Last Modified: {format_date(file_stat.st_mtime)}")
        print(f"  Last Accessed: {format_date(file_stat.st_atime)}")
        print()

    except IOError as e:
        if "No such file" in str(e) or e.errno == 2:
            print(f"Error: Path not found: {remote_path}")
        elif "Permission denied" in str(e) or e.errno == 13:
            print(f"Error: Permission denied: {remote_path}")
        else:
            print(f"Error getting info: {e}")
        sys.exit(1)


def cmd_rm(sftp, args):
    """Delete a remote file."""
    remote_path = args.path

    try:
        # Check if it's a file
        file_stat = sftp.stat(remote_path)
        if stat.S_ISDIR(file_stat.st_mode):
            print(f"Error: {remote_path} is a directory")
            print("Use 'rmdir' to remove directories")
            sys.exit(1)

        # Confirm deletion
        if not args.yes:
            confirm = input(f"Delete {remote_path}? [y/N] ")
            if confirm.lower() != "y":
                print("Cancelled")
                return

        sftp.remove(remote_path)
        print(f"Deleted: {remote_path}")

    except IOError as e:
        if "No such file" in str(e) or e.errno == 2:
            print(f"Error: File not found: {remote_path}")
        elif "Permission denied" in str(e) or e.errno == 13:
            print(f"Error: Permission denied: {remote_path}")
        else:
            print(f"Error deleting file: {e}")
        sys.exit(1)


def cmd_mkdir(sftp, args):
    """Create a remote directory."""
    remote_path = args.path

    try:
        sftp.mkdir(remote_path)
        print(f"Created directory: {remote_path}")

    except IOError as e:
        if "File exists" in str(e) or e.errno == 17:
            print(f"Error: Directory already exists: {remote_path}")
        elif "No such file" in str(e) or e.errno == 2:
            print(f"Error: Parent directory not found: {remote_path}")
        elif "Permission denied" in str(e) or e.errno == 13:
            print(f"Error: Permission denied: {remote_path}")
        else:
            print(f"Error creating directory: {e}")
        sys.exit(1)


def cmd_rmdir(sftp, args):
    """Remove a remote directory (must be empty)."""
    remote_path = args.path

    try:
        # Check if it's a directory
        file_stat = sftp.stat(remote_path)
        if not stat.S_ISDIR(file_stat.st_mode):
            print(f"Error: {remote_path} is not a directory")
            print("Use 'rm' to remove files")
            sys.exit(1)

        # Confirm deletion
        if not args.yes:
            confirm = input(f"Remove directory {remote_path}? [y/N] ")
            if confirm.lower() != "y":
                print("Cancelled")
                return

        sftp.rmdir(remote_path)
        print(f"Removed directory: {remote_path}")

    except IOError as e:
        if "No such file" in str(e) or e.errno == 2:
            print(f"Error: Directory not found: {remote_path}")
        elif "Permission denied" in str(e) or e.errno == 13:
            print(f"Error: Permission denied: {remote_path}")
        elif "Directory not empty" in str(e) or e.errno == 39:
            print(f"Error: Directory not empty: {remote_path}")
            print("Remove all files from the directory first")
        else:
            print(f"Error removing directory: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Access remote SFTP servers for file operations.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s ls /path/to/directory
  %(prog)s get /path/to/file.txt
  %(prog)s get /path/to/file.txt --output local.txt
  %(prog)s put local.txt /remote/path/file.txt
  %(prog)s info /path/to/file.txt
  %(prog)s rm /path/to/file.txt
  %(prog)s mkdir /path/to/new/directory
  %(prog)s rmdir /path/to/directory
        """,
    )

    # Common arguments
    parser.add_argument("--host", "-H", help="SFTP server hostname")
    parser.add_argument("--port", "-P", type=int, help="SFTP server port (default: 22)")
    parser.add_argument("--user", "-u", help="Username for authentication")
    parser.add_argument("--password", "-p", help="Password (prefer using .credentials file)")
    parser.add_argument("--key", "-k", help="Path to SSH private key file")
    parser.add_argument("--timeout", "-t", type=int, default=30, help="Connection timeout in seconds")

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # ls command
    ls_parser = subparsers.add_parser("ls", help="List remote directory")
    ls_parser.add_argument("path", nargs="?", default=".", help="Remote directory path")

    # get command
    get_parser = subparsers.add_parser("get", help="Get file contents or download")
    get_parser.add_argument("path", help="Remote file path")
    get_parser.add_argument("--output", "-o", help="Output file path")

    # put command
    put_parser = subparsers.add_parser("put", help="Upload a file")
    put_parser.add_argument("local", help="Local file path")
    put_parser.add_argument("dest", help="Remote destination path")

    # info command
    info_parser = subparsers.add_parser("info", help="Get file/directory metadata")
    info_parser.add_argument("path", help="Remote path")

    # rm command
    rm_parser = subparsers.add_parser("rm", help="Delete a remote file")
    rm_parser.add_argument("path", help="Remote file path")
    rm_parser.add_argument("--yes", "-y", action="store_true", help="Skip confirmation")

    # mkdir command
    mkdir_parser = subparsers.add_parser("mkdir", help="Create remote directory")
    mkdir_parser.add_argument("path", help="Remote directory path")

    # rmdir command
    rmdir_parser = subparsers.add_parser("rmdir", help="Remove remote directory")
    rmdir_parser.add_argument("path", help="Remote directory path")
    rmdir_parser.add_argument("--yes", "-y", action="store_true", help="Skip confirmation")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Load credentials and create client
    creds = load_credentials()
    transport, sftp = get_sftp_client(
        creds,
        host=args.host,
        port=args.port,
        user=args.user,
        password=args.password,
        key_file=args.key,
        timeout=args.timeout,
    )

    try:
        # Execute command
        if args.command == "ls":
            cmd_ls(sftp, args)
        elif args.command == "get":
            cmd_get(sftp, args)
        elif args.command == "put":
            cmd_put(sftp, args)
        elif args.command == "info":
            cmd_info(sftp, args)
        elif args.command == "rm":
            cmd_rm(sftp, args)
        elif args.command == "mkdir":
            cmd_mkdir(sftp, args)
        elif args.command == "rmdir":
            cmd_rmdir(sftp, args)
    finally:
        # Clean up connections
        sftp.close()
        transport.close()


if __name__ == "__main__":
    main()
