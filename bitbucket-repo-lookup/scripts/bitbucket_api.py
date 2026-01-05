#!/usr/bin/env python3
"""
Bitbucket Repository Lookup Helper

A utility script for interacting with the Bitbucket Cloud REST API.
Provides functionality for listing, searching, and cloning repositories.

Usage:
    python bitbucket_api.py list --workspace WORKSPACE [options]
    python bitbucket_api.py search --workspace WORKSPACE --query QUERY [options]
    python bitbucket_api.py clone --workspace WORKSPACE --repos REPO1,REPO2 [options]
    python bitbucket_api.py info --workspace WORKSPACE --repo REPO

Environment Variables:
    BITBUCKET_USERNAME     - Bitbucket username
    BITBUCKET_APP_PASSWORD - Bitbucket app password

Examples:
    # List all repositories
    python bitbucket_api.py list --workspace acme-corp

    # Search for Python repositories
    python bitbucket_api.py list --workspace acme-corp --language python

    # Clone specific repositories
    python bitbucket_api.py clone --workspace acme-corp --repos user-service,payment-gateway

    # Get repository info
    python bitbucket_api.py info --workspace acme-corp --repo user-service
"""

import argparse
import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from urllib.parse import quote, urlencode

# Check for requests library
try:
    import requests
except ImportError:
    print("Error: 'requests' library is required. Install with: pip install requests")
    sys.exit(1)


# Constants
API_BASE_URL = "https://api.bitbucket.org/2.0"
DEFAULT_PAGE_SIZE = 50
MAX_RETRIES = 3
RETRY_DELAY = 2


@dataclass
class Repository:
    """Represents a Bitbucket repository."""
    name: str
    slug: str
    full_name: str
    description: str
    language: str
    project_key: str
    project_name: str
    size: int
    is_private: bool
    main_branch: str
    created_on: str
    updated_on: str
    clone_url_https: str
    clone_url_ssh: str
    html_url: str

    @classmethod
    def from_api_response(cls, data: dict) -> "Repository":
        """Create Repository from Bitbucket API response."""
        project = data.get("project", {})
        mainbranch = data.get("mainbranch", {})

        # Extract clone URLs
        clone_urls = {c["name"]: c["href"] for c in data.get("links", {}).get("clone", [])}

        return cls(
            name=data.get("name", ""),
            slug=data.get("slug", ""),
            full_name=data.get("full_name", ""),
            description=data.get("description", "") or "",
            language=data.get("language", "") or "N/A",
            project_key=project.get("key", "N/A"),
            project_name=project.get("name", "N/A"),
            size=data.get("size", 0),
            is_private=data.get("is_private", True),
            main_branch=mainbranch.get("name", "main"),
            created_on=data.get("created_on", ""),
            updated_on=data.get("updated_on", ""),
            clone_url_https=clone_urls.get("https", ""),
            clone_url_ssh=clone_urls.get("ssh", ""),
            html_url=data.get("links", {}).get("html", {}).get("href", ""),
        )

    @property
    def size_mb(self) -> float:
        """Return size in megabytes."""
        return round(self.size / (1024 * 1024), 1)

    @property
    def updated_date(self) -> str:
        """Return formatted update date."""
        if not self.updated_on:
            return "N/A"
        try:
            dt = datetime.fromisoformat(self.updated_on.replace("Z", "+00:00"))
            return dt.strftime("%Y-%m-%d")
        except (ValueError, AttributeError):
            return "N/A"

    @property
    def created_date(self) -> str:
        """Return formatted creation date."""
        if not self.created_on:
            return "N/A"
        try:
            dt = datetime.fromisoformat(self.created_on.replace("Z", "+00:00"))
            return dt.strftime("%Y-%m-%d")
        except (ValueError, AttributeError):
            return "N/A"


class BitbucketAPIError(Exception):
    """Custom exception for Bitbucket API errors."""
    def __init__(self, message: str, status_code: int = None, response: dict = None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class BitbucketClient:
    """Client for interacting with the Bitbucket Cloud REST API."""

    def __init__(self, username: str, app_password: str, base_url: str = API_BASE_URL):
        self.username = username
        self.app_password = app_password
        self.base_url = base_url
        self.session = requests.Session()
        self.session.auth = (username, app_password)
        self.session.headers.update({
            "Accept": "application/json",
            "Content-Type": "application/json",
        })

    def _make_request(self, method: str, url: str, **kwargs) -> dict:
        """Make an API request with retry logic."""
        for attempt in range(MAX_RETRIES):
            try:
                response = self.session.request(method, url, **kwargs)

                if response.status_code == 429:
                    # Rate limited
                    retry_after = int(response.headers.get("Retry-After", 60))
                    print(f"Rate limited. Waiting {retry_after} seconds...", file=sys.stderr)
                    time.sleep(retry_after)
                    continue

                if response.status_code == 401:
                    raise BitbucketAPIError(
                        "Authentication failed. Check your username and app password.",
                        status_code=401
                    )

                if response.status_code == 403:
                    raise BitbucketAPIError(
                        "Access forbidden. Check your permissions.",
                        status_code=403
                    )

                if response.status_code == 404:
                    raise BitbucketAPIError(
                        "Resource not found. Check workspace/repository name.",
                        status_code=404
                    )

                if response.status_code >= 500:
                    if attempt < MAX_RETRIES - 1:
                        time.sleep(RETRY_DELAY * (attempt + 1))
                        continue
                    raise BitbucketAPIError(
                        f"Bitbucket server error: {response.status_code}",
                        status_code=response.status_code
                    )

                response.raise_for_status()
                return response.json()

            except requests.RequestException as e:
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY * (attempt + 1))
                    continue
                raise BitbucketAPIError(f"Request failed: {str(e)}")

        raise BitbucketAPIError("Max retries exceeded")

    def list_repositories(
        self,
        workspace: str,
        project: Optional[str] = None,
        language: Optional[str] = None,
        name_contains: Optional[str] = None,
        sort: str = "-updated_on",
        page_size: int = DEFAULT_PAGE_SIZE,
        max_results: int = None,
    ) -> list[Repository]:
        """
        List repositories in a workspace with optional filters.

        Args:
            workspace: Bitbucket workspace slug
            project: Filter by project key
            language: Filter by programming language
            name_contains: Filter by name (fuzzy match)
            sort: Sort field (prefix with - for descending)
            page_size: Number of results per page
            max_results: Maximum total results to return

        Returns:
            List of Repository objects
        """
        # Build query filter
        query_parts = []
        if project:
            query_parts.append(f'project.key = "{project}"')
        if language:
            query_parts.append(f'language = "{language.lower()}"')
        if name_contains:
            query_parts.append(f'name ~ "{name_contains}"')

        query = " AND ".join(query_parts) if query_parts else None

        # Build URL parameters
        params = {"pagelen": page_size, "sort": sort}
        if query:
            params["q"] = query

        url = f"{self.base_url}/repositories/{quote(workspace)}"
        repositories = []

        while url:
            if max_results and len(repositories) >= max_results:
                break

            data = self._make_request("GET", url, params=params)
            params = {}  # Clear params for subsequent pages (next URL includes them)

            for repo_data in data.get("values", []):
                if max_results and len(repositories) >= max_results:
                    break
                repositories.append(Repository.from_api_response(repo_data))

            url = data.get("next")

        return repositories

    def get_repository(self, workspace: str, repo_slug: str) -> Repository:
        """
        Get details for a specific repository.

        Args:
            workspace: Bitbucket workspace slug
            repo_slug: Repository slug

        Returns:
            Repository object
        """
        url = f"{self.base_url}/repositories/{quote(workspace)}/{quote(repo_slug)}"
        data = self._make_request("GET", url)
        return Repository.from_api_response(data)

    def get_latest_commit(self, workspace: str, repo_slug: str) -> dict:
        """
        Get the latest commit for a repository.

        Args:
            workspace: Bitbucket workspace slug
            repo_slug: Repository slug

        Returns:
            Commit information dict
        """
        url = f"{self.base_url}/repositories/{quote(workspace)}/{quote(repo_slug)}/commits"
        data = self._make_request("GET", url, params={"pagelen": 1})

        commits = data.get("values", [])
        if not commits:
            return {}

        commit = commits[0]
        return {
            "hash": commit.get("hash", "")[:7],
            "message": commit.get("message", "").split("\n")[0][:50],
            "author": commit.get("author", {}).get("user", {}).get("display_name", "Unknown"),
            "date": commit.get("date", ""),
        }

    def clone_repository(
        self,
        repo: Repository,
        destination: str,
        method: str = "https",
        depth: int = 0,
    ) -> tuple[bool, str]:
        """
        Clone a repository to the local filesystem.

        Args:
            repo: Repository to clone
            destination: Destination directory
            method: Clone method ('https' or 'ssh')
            depth: Clone depth (0 for full clone)

        Returns:
            Tuple of (success: bool, message: str)
        """
        clone_url = repo.clone_url_https if method == "https" else repo.clone_url_ssh

        if not clone_url:
            return False, f"No {method} clone URL available"

        # For HTTPS, embed credentials in URL
        if method == "https" and self.username and self.app_password:
            clone_url = clone_url.replace(
                "https://",
                f"https://{quote(self.username)}:{quote(self.app_password)}@"
            )

        # Build git clone command
        cmd = ["git", "clone"]
        if depth > 0:
            cmd.extend(["--depth", str(depth)])
        cmd.extend([clone_url, destination])

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            if result.returncode == 0:
                return True, f"Cloned to {destination}"
            else:
                error_msg = result.stderr.strip() or result.stdout.strip()
                return False, f"Clone failed: {error_msg}"

        except subprocess.TimeoutExpired:
            return False, "Clone timed out after 5 minutes"
        except Exception as e:
            return False, f"Clone error: {str(e)}"


def format_table(repositories: list[Repository], verbose: bool = False) -> str:
    """Format repositories as a table."""
    if not repositories:
        return "No repositories found."

    lines = []

    if verbose:
        for i, repo in enumerate(repositories, 1):
            lines.append(f"\n{'─' * 70}")
            lines.append(f"{i}. {repo.name}")
            lines.append(f"{'─' * 70}")
            lines.append(f"   Project:     {repo.project_name} ({repo.project_key})")
            lines.append(f"   Description: {repo.description[:50] + '...' if len(repo.description) > 50 else repo.description or 'N/A'}")
            lines.append(f"   Language:    {repo.language}")
            lines.append(f"   Size:        {repo.size_mb} MB")
            lines.append(f"   Main Branch: {repo.main_branch}")
            lines.append(f"   Updated:     {repo.updated_date}")
            lines.append(f"   Private:     {'Yes' if repo.is_private else 'No'}")
            lines.append(f"   URL:         {repo.html_url}")
    else:
        # Header
        lines.append("┌─────┬──────────────────────────┬────────────┬────────────┬────────────┐")
        lines.append("│  #  │ Repository               │ Project    │ Language   │ Updated    │")
        lines.append("├─────┼──────────────────────────┼────────────┼────────────┼────────────┤")

        for i, repo in enumerate(repositories, 1):
            name = repo.name[:24] + ".." if len(repo.name) > 24 else repo.name
            project = repo.project_key[:10] if repo.project_key else "N/A"
            language = repo.language[:10] if repo.language else "N/A"
            updated = repo.updated_date

            lines.append(f"│ {i:3} │ {name:<24} │ {project:<10} │ {language:<10} │ {updated:<10} │")

        lines.append("└─────┴──────────────────────────┴────────────┴────────────┴────────────┘")

    lines.append(f"\nFound {len(repositories)} repositories.")
    return "\n".join(lines)


def format_json(repositories: list[Repository]) -> str:
    """Format repositories as JSON."""
    data = []
    for repo in repositories:
        data.append({
            "name": repo.name,
            "slug": repo.slug,
            "full_name": repo.full_name,
            "description": repo.description,
            "language": repo.language,
            "project": {
                "key": repo.project_key,
                "name": repo.project_name,
            },
            "size_mb": repo.size_mb,
            "is_private": repo.is_private,
            "main_branch": repo.main_branch,
            "updated_on": repo.updated_date,
            "created_on": repo.created_date,
            "urls": {
                "html": repo.html_url,
                "clone_https": repo.clone_url_https,
                "clone_ssh": repo.clone_url_ssh,
            },
        })
    return json.dumps(data, indent=2)


def main():
    parser = argparse.ArgumentParser(
        description="Bitbucket Repository Lookup Helper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # List command
    list_parser = subparsers.add_parser("list", help="List repositories")
    list_parser.add_argument("--workspace", "-w", required=True, help="Workspace slug")
    list_parser.add_argument("--project", "-p", help="Filter by project key")
    list_parser.add_argument("--language", "-l", help="Filter by language")
    list_parser.add_argument("--search", "-s", help="Search by name")
    list_parser.add_argument("--sort", default="-updated_on", help="Sort field (default: -updated_on)")
    list_parser.add_argument("--limit", type=int, help="Maximum results")
    list_parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    list_parser.add_argument("--json", action="store_true", help="Output as JSON")

    # Info command
    info_parser = subparsers.add_parser("info", help="Get repository info")
    info_parser.add_argument("--workspace", "-w", required=True, help="Workspace slug")
    info_parser.add_argument("--repo", "-r", required=True, help="Repository slug")
    info_parser.add_argument("--json", action="store_true", help="Output as JSON")

    # Clone command
    clone_parser = subparsers.add_parser("clone", help="Clone repositories")
    clone_parser.add_argument("--workspace", "-w", required=True, help="Workspace slug")
    clone_parser.add_argument("--repos", "-r", required=True, help="Comma-separated repo slugs")
    clone_parser.add_argument("--dest", "-d", default=".", help="Destination directory")
    clone_parser.add_argument("--method", "-m", choices=["https", "ssh"], default="https", help="Clone method")
    clone_parser.add_argument("--depth", type=int, default=0, help="Clone depth (0 for full)")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Get credentials from environment
    username = os.environ.get("BITBUCKET_USERNAME")
    app_password = os.environ.get("BITBUCKET_APP_PASSWORD")

    if not username or not app_password:
        print("Error: Set BITBUCKET_USERNAME and BITBUCKET_APP_PASSWORD environment variables", file=sys.stderr)
        sys.exit(1)

    try:
        client = BitbucketClient(username, app_password)

        if args.command == "list":
            repos = client.list_repositories(
                workspace=args.workspace,
                project=args.project,
                language=args.language,
                name_contains=args.search,
                sort=args.sort,
                max_results=args.limit,
            )

            if args.json:
                print(format_json(repos))
            else:
                print(format_table(repos, verbose=args.verbose))

        elif args.command == "info":
            repo = client.get_repository(args.workspace, args.repo)
            commit = client.get_latest_commit(args.workspace, args.repo)

            if args.json:
                print(format_json([repo]))
            else:
                print(f"\nRepository: {repo.name}")
                print(f"{'─' * 50}")
                print(f"Full Name:   {repo.full_name}")
                print(f"Description: {repo.description or 'N/A'}")
                print(f"Project:     {repo.project_name} ({repo.project_key})")
                print(f"Language:    {repo.language}")
                print(f"Size:        {repo.size_mb} MB")
                print(f"Main Branch: {repo.main_branch}")
                print(f"Private:     {'Yes' if repo.is_private else 'No'}")
                print(f"Created:     {repo.created_date}")
                print(f"Updated:     {repo.updated_date}")
                print(f"URL:         {repo.html_url}")
                if commit:
                    print(f"\nLatest Commit:")
                    print(f"  {commit['hash']} - {commit['message']}")
                    print(f"  by {commit['author']}")
                print(f"\nClone (HTTPS): git clone {repo.clone_url_https}")
                print(f"Clone (SSH):   git clone {repo.clone_url_ssh}")

        elif args.command == "clone":
            repo_slugs = [r.strip() for r in args.repos.split(",")]
            dest_base = os.path.expanduser(args.dest)

            success_count = 0
            failed = []

            for slug in repo_slugs:
                print(f"\nCloning {slug}...")
                try:
                    repo = client.get_repository(args.workspace, slug)
                    dest = os.path.join(dest_base, slug)

                    if os.path.exists(dest):
                        print(f"  ⚠ Skipped: Directory already exists at {dest}")
                        continue

                    success, message = client.clone_repository(
                        repo, dest, method=args.method, depth=args.depth
                    )

                    if success:
                        print(f"  ✓ {message}")
                        success_count += 1
                    else:
                        print(f"  ✗ {message}")
                        failed.append((slug, message))

                except BitbucketAPIError as e:
                    print(f"  ✗ {str(e)}")
                    failed.append((slug, str(e)))

            print(f"\n{'═' * 50}")
            print(f"Summary: {success_count}/{len(repo_slugs)} repositories cloned")
            if failed:
                print(f"\nFailed:")
                for slug, error in failed:
                    print(f"  • {slug}: {error}")

    except BitbucketAPIError as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nOperation cancelled.", file=sys.stderr)
        sys.exit(130)


if __name__ == "__main__":
    main()
