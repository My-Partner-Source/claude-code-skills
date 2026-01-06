#!/usr/bin/env python3
"""
Interactive Credential Setup Helper

Parses .credentials.example templates and prompts users for values,
creating .credentials files with proper permissions.

Usage:
    # Auto-discover template for a skill
    python setup_credentials.py --skill bitbucket-repo-lookup

    # Custom paths
    python setup_credentials.py --example path/to/.credentials.example --output path/to/.credentials

    # Dry run (preview only)
    python setup_credentials.py --skill bitbucket-repo-lookup --dry-run

Examples:
    python setup_credentials.py --skill bitbucket-repo-lookup
    python setup_credentials.py --example ~/custom/.credentials.example --output ~/.credentials
    python setup_credentials.py --skill my-skill --backup --dry-run
"""

import argparse
import getpass
import os
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional


def find_skill_template(skill_name: str) -> Optional[Path]:
    """
    Find .credentials.example for a given skill name.

    Searches in: skill-name/references/.credentials.example

    Args:
        skill_name: Name of the skill (e.g., 'bitbucket-repo-lookup')

    Returns:
        Path to .credentials.example or None if not found
    """
    # Get the repository root (assuming script is in credential-setup/scripts/)
    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parent.parent

    # Look for skill directory
    skill_dir = repo_root / skill_name
    if not skill_dir.exists():
        return None

    # Look for .credentials.example in references/
    template_path = skill_dir / "references" / ".credentials.example"
    if template_path.exists():
        return template_path

    return None


def parse_credentials_template(template_path: Path) -> List[Dict]:
    """
    Parse .credentials.example file to extract required variables.

    Parsing rules:
    - Find lines matching: export VAR_NAME="value"
    - Ignore commented lines (starting with #)
    - Extract variable name, placeholder value
    - Capture surrounding comments for context

    Args:
        template_path: Path to .credentials.example

    Returns:
        List of credential specifications:
        [
            {
                'variable': 'BITBUCKET_USERNAME',
                'placeholder': 'your-username-here',
                'context': 'Option 1: App Password (Recommended)',
                'required': True,
                'line_number': 5
            },
            ...
        ]
    """
    credentials = []
    lines = template_path.read_text().splitlines()

    # Pattern to match: export VAR_NAME="value"
    export_pattern = re.compile(r'^export\s+([A-Z_][A-Z0-9_]*)\s*=\s*"([^"]*)"')

    # Track context (comments above exports)
    context_buffer = []

    for line_num, line in enumerate(lines, start=1):
        stripped = line.strip()

        # Commented line - might be context or commented export
        if stripped.startswith('#'):
            # Check if it's a commented export (optional credential)
            commented_export = re.match(r'#\s*export\s+([A-Z_][A-Z0-9_]*)\s*=\s*"([^"]*)"', stripped)
            if commented_export:
                var_name, placeholder = commented_export.groups()
                credentials.append({
                    'variable': var_name,
                    'placeholder': placeholder,
                    'context': ' '.join(context_buffer),
                    'required': False,
                    'line_number': line_num
                })
                context_buffer = []
            else:
                # Regular comment - add to context buffer
                comment_text = stripped.lstrip('#').strip()
                if comment_text and not comment_text.startswith('='):
                    context_buffer.append(comment_text)

        # Active export statement
        elif export_pattern.match(stripped):
            match = export_pattern.match(stripped)
            var_name, placeholder = match.groups()

            credentials.append({
                'variable': var_name,
                'placeholder': placeholder,
                'context': ' '.join(context_buffer),
                'required': True,
                'line_number': line_num
            })
            context_buffer = []

        # Empty line or other content - clear context buffer
        elif not stripped:
            context_buffer = []

    return credentials


def prompt_for_credentials(credentials_spec: List[Dict]) -> Dict[str, str]:
    """
    Interactively prompt user for each credential.

    Args:
        credentials_spec: List of credential specifications from parse_credentials_template

    Returns:
        Dict mapping variable names to user-provided values
        Only includes credentials the user chose to provide
    """
    print("\n" + "="*60)
    print("  Interactive Credential Setup")
    print("="*60 + "\n")

    required_creds = [c for c in credentials_spec if c['required']]
    optional_creds = [c for c in credentials_spec if not c['required']]

    print(f"Found {len(required_creds)} required credential(s)")
    if optional_creds:
        print(f"Found {len(optional_creds)} optional credential(s)\n")
    else:
        print()

    values = {}

    # Prompt for required credentials
    for cred in required_creds:
        if cred['context']:
            print(f"[{cred['context']}]")

        prompt = f"{cred['variable']}"
        if cred['placeholder'] and cred['placeholder'] not in ['', 'your-value-here']:
            prompt += f" (hint: {cred['placeholder']})"
        prompt += ": "

        # Use getpass for PASSWORD, TOKEN, SECRET, KEY in variable name
        sensitive_keywords = ['PASSWORD', 'TOKEN', 'SECRET', 'KEY', 'CREDENTIALS']
        is_sensitive = any(keyword in cred['variable'] for keyword in sensitive_keywords)

        while True:
            if is_sensitive:
                value = getpass.getpass(prompt)
            else:
                value = input(prompt)

            if value.strip():
                values[cred['variable']] = value.strip()
                break
            else:
                print("  ❌ Value cannot be empty. Please try again.")

        print()  # Blank line after each credential

    # Handle optional credentials
    if optional_creds:
        print("\nOptional credentials (currently commented):")
        for cred in optional_creds:
            print(f"  - {cred['variable']}")

        enable_optional = input("\nEnable any optional credentials? [y/N]: ").strip().lower()

        if enable_optional in ['y', 'yes']:
            for cred in optional_creds:
                if cred['context']:
                    print(f"\n[{cred['context']}]")

                prompt = f"{cred['variable']}"
                if cred['placeholder']:
                    prompt += f" (hint: {cred['placeholder']})"
                prompt += " (leave empty to skip): "

                # Check if sensitive
                is_sensitive = any(keyword in cred['variable'] for keyword in sensitive_keywords)

                if is_sensitive:
                    value = getpass.getpass(prompt)
                else:
                    value = input(prompt)

                if value.strip():
                    values[cred['variable']] = value.strip()

    return values


def create_credentials_file(output_path: Path, template_path: Path,
                              credentials: Dict[str, str], dry_run: bool = False) -> bool:
    """
    Create .credentials file with user-provided values.

    Args:
        output_path: Where to write .credentials
        template_path: Original .credentials.example for structure
        credentials: Dict of variable names to values
        dry_run: If True, only preview without creating

    Returns:
        True if successful, False otherwise
    """
    # Read template to preserve structure and comments
    template_lines = template_path.read_text().splitlines()

    output_lines = []
    output_lines.append("# Credentials File")
    output_lines.append(f"# Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    output_lines.append("# DO NOT commit this file - it's in .gitignore")
    output_lines.append("")

    # Pattern to match exports
    export_pattern = re.compile(r'^(#\s*)?export\s+([A-Z_][A-Z0-9_]*)\s*=\s*"([^"]*)"')

    for line in template_lines:
        stripped = line.strip()

        # Skip the template header comments (up to first blank line or export)
        if output_lines and len(output_lines) <= 4:
            if stripped.startswith('#') and 'SECURITY' in stripped:
                continue
            if stripped.startswith('#') and ('Copy' in stripped or 'DO NOT commit' in stripped):
                continue

        match = export_pattern.match(stripped)
        if match:
            commented, var_name, _ = match.groups()

            if var_name in credentials:
                # User provided a value - write as active export
                value = credentials[var_name]
                output_lines.append(f'export {var_name}="{value}"')
            else:
                # User didn't provide - keep commented
                output_lines.append(line)
        else:
            # Preserve comments and other lines
            output_lines.append(line)

    output_content = '\n'.join(output_lines) + '\n'

    if dry_run:
        print("\n" + "="*60)
        print("  DRY RUN - Preview of .credentials file:")
        print("="*60)
        print(output_content)
        print("="*60)
        print(f"\nWould be written to: {output_path}")
        print("(No file was actually created)")
        return True

    # Create the file
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(output_content)

        # Set permissions to 600 (owner read/write only)
        os.chmod(output_path, 0o600)

        print(f"\n✓ File created: {output_path}")
        print(f"✓ Permissions set to 600 (owner read/write only)")

        return True

    except Exception as e:
        print(f"\n❌ Error creating file: {e}")
        return False


def validate_gitignore(credentials_path: Path) -> None:
    """
    Warn if .credentials isn't in .gitignore.

    Args:
        credentials_path: Path to .credentials file
    """
    # Find repository root (.git directory)
    current = credentials_path.parent
    git_root = None

    while current != current.parent:
        if (current / '.git').exists():
            git_root = current
            break
        current = current.parent

    if not git_root:
        print("⚠️  Warning: Not in a git repository")
        return

    gitignore_path = git_root / '.gitignore'
    if not gitignore_path.exists():
        print(f"⚠️  Warning: No .gitignore found at {git_root}")
        print("   Consider adding .credentials to .gitignore")
        return

    gitignore_content = gitignore_path.read_text()
    if '.credentials' in gitignore_content:
        print("✓ Validated: .credentials is in .gitignore")
    else:
        print("⚠️  Warning: .credentials not found in .gitignore")
        print(f"   Add this to {gitignore_path}:")
        print("   # Credentials (NEVER commit these)")
        print("   .credentials")


def main():
    parser = argparse.ArgumentParser(
        description="Interactive credential setup helper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --skill bitbucket-repo-lookup
  %(prog)s --example path/to/.credentials.example --output path/to/.credentials
  %(prog)s --skill my-skill --dry-run
        """
    )

    parser.add_argument('--skill', help='Skill name (auto-finds .credentials.example)')
    parser.add_argument('--example', type=Path, help='Path to .credentials.example')
    parser.add_argument('--output', type=Path, help='Output path for .credentials')
    parser.add_argument('--dry-run', action='store_true', help='Preview without creating')
    parser.add_argument('--backup', action='store_true', help='Backup existing .credentials')

    args = parser.parse_args()

    # Determine template path
    if args.skill:
        template_path = find_skill_template(args.skill)
        if not template_path:
            print(f"❌ Error: Could not find .credentials.example for skill '{args.skill}'")
            print(f"   Expected location: {args.skill}/references/.credentials.example")
            sys.exit(1)

        # Default output path
        if not args.output:
            args.output = template_path.parent / '.credentials'

        print(f"Setting up credentials for {args.skill}...\n")

    elif args.example:
        template_path = args.example
        if not template_path.exists():
            print(f"❌ Error: Template not found: {template_path}")
            sys.exit(1)

        # Default output to same directory
        if not args.output:
            args.output = template_path.parent / '.credentials'

    else:
        parser.print_help()
        sys.exit(1)

    # Check if output file already exists
    if args.output.exists() and not args.dry_run:
        if args.backup:
            backup_path = args.output.parent / f".credentials.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copy2(args.output, backup_path)
            print(f"✓ Backed up existing file to: {backup_path}\n")
        else:
            confirm = input(f"⚠️  File already exists: {args.output}\n   Overwrite? [y/N]: ")
            if confirm.strip().lower() not in ['y', 'yes']:
                print("Cancelled.")
                sys.exit(0)
            print()

    # Parse template
    try:
        credentials_spec = parse_credentials_template(template_path)
    except Exception as e:
        print(f"❌ Error parsing template: {e}")
        sys.exit(1)

    if not credentials_spec:
        print(f"❌ No credentials found in template: {template_path}")
        print("   Template should contain lines like: export VAR_NAME=\"value\"")
        sys.exit(1)

    # Prompt for values
    try:
        user_values = prompt_for_credentials(credentials_spec)
    except KeyboardInterrupt:
        print("\n\nCancelled by user.")
        sys.exit(0)

    # Create file
    print("\nCreating .credentials file...")
    success = create_credentials_file(args.output, template_path, user_values, args.dry_run)

    if not success:
        sys.exit(1)

    # Validate gitignore
    if not args.dry_run:
        validate_gitignore(args.output)

    # Success message
    print(f"\n{'='*60}")
    print("  Setup complete!")
    print("="*60)

    if not args.dry_run:
        print(f"\nTo use these credentials:")
        print(f"  source {args.output}")
    else:
        print("\n(This was a dry run - no file was created)")

    sys.exit(0)


if __name__ == "__main__":
    main()
