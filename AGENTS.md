# AGENTS.md

This file provides AI coding assistants with essential context about the codebase structure, conventions, and workflows.

## Project Overview

**claude-code-skills** is a collection of three specialized skills designed to streamline development workflows:

1. **code-journey-documenter** - Transform coding sessions into book chapters for "Code With Claude: How AI Transformed the Way I Work (And Think)"
2. **social-media-poster** - Convert development insights into authentic X/Twitter and LinkedIn posts
3. **bitbucket-repo-lookup** - Discover, search, and clone Bitbucket repositories without leaving your development environment

This is **not a traditional monolithic application**. Instead, it's a skill marketplace where each skill is independently functional yet follows consistent organizational patterns. Skills are designed for integration with AI-assisted development tools and can be invoked individually.

**Target Users:** Developers documenting their AI-assisted development journey, building authentic technical audiences, or managing cloud repositories.

**Philosophy:** Document mastery through doing (actual work), reflecting (what worked/failed), and teaching (distillable patterns).

---

## Tech Stack

| Technology | Purpose |
|------------|---------|
| **Python 3.x** | Utility scripts for parsing, validation, API integration |
| **Markdown** | Content format for templates, documentation, sessions, posts |
| **YAML Frontmatter** | Metadata in SKILL.md files and content templates |
| **Git** | Version control and repository cloning |
| **Bitbucket Cloud REST API v2.0** | Repository discovery and management (Cloud instances) |
| **Bitbucket Server REST API v1.0** | Repository discovery and management (Server/Data Center instances) |

**Dependencies:**
- Python 3 standard library (all skills)
- `requests` library (bitbucket-repo-lookup only)

---

## Repository Structure

```
claude-code-skills/
├── README.md                              # User-facing documentation
├── LICENSE                                # MIT License
├── .gitignore                            # Git ignore patterns
│
├── code-journey-documenter/
│   ├── SKILL.md                          # Skill definition
│   ├── assets/
│   │   └── chapter-templates/
│   │       ├── foundation-chapter.md     # Part I: Foundations template
│   │       ├── job-story-chapter.md      # Part II: Job Stories template
│   │       └── meta-chapter.md           # Part III: Meta-reflections template
│   ├── references/
│   │   ├── config.md                     # Path configuration
│   │   ├── book-structure.md             # Complete 13-chapter book outline
│   │   ├── pattern-library.md            # Collected transferable patterns
│   │   └── session-template.md           # Session logging format
│   └── scripts/
│       └── format_session.py             # Session → Chapter converter (7.5KB)
│
├── social-media-poster/
│   ├── SKILL.md                          # Skill definition
│   ├── assets/
│   │   └── templates/
│   │       ├── x-single.md               # Single tweet template (280 char)
│   │       ├── x-thread.md               # Twitter thread template
│   │       └── linkedin.md               # LinkedIn post template (3,000 char)
│   ├── references/
│   │   ├── config.md                     # Path configuration
│   │   ├── platform-x.md                 # X/Twitter best practices
│   │   ├── platform-linkedin.md          # LinkedIn best practices
│   │   └── voice-guide.md                # Writing voice and tone guidelines
│   └── scripts/
│       └── validate_post.py              # Platform-specific post validator (6.6KB)
│
└── bitbucket-repo-lookup/
    ├── SKILL.md                          # Skill definition
    ├── assets/
    │   └── templates/
    │       ├── repo-list.md              # Repository listing template
    │       └── clone-summary.md          # Clone operation summary template
    ├── references/
    │   ├── config.md                     # Auth and path configuration
    │   └── api-guide.md                  # Bitbucket API reference
    └── scripts/
        └── bitbucket_api.py              # Bitbucket Cloud API wrapper (21KB)
```

---

## Skills Summary

| Skill | Purpose | Key Files | Entry Point |
|-------|---------|-----------|-------------|
| **code-journey-documenter** | Parse session logs → structured chapter drafts | `format_session.py`<br>`book-structure.md`<br>`session-template.md` | `/code-journey-documenter` |
| **social-media-poster** | Validate posts for X/LinkedIn | `validate_post.py`<br>`voice-guide.md`<br>`platform-*.md` | `/social-media-poster` |
| **bitbucket-repo-lookup** | List/search/clone Bitbucket repos | `bitbucket_api.py`<br>`config.md`<br>`api-guide.md` | `/bitbucket-repo-lookup` |

---

## Directory Conventions

All three skills follow an **identical organizational pattern**:

```
[skill-name]/
├── SKILL.md              # Skill definition with YAML frontmatter
├── assets/               # Templates for content generation
│   └── templates/        # Platform/format-specific templates
├── references/           # Configuration and documentation
│   └── config.md        # User-configurable settings (NEVER commit with real credentials)
└── scripts/             # Python utilities (executable with #!/usr/bin/env python3)
```

### Directory Purposes

| Directory | Purpose | Examples |
|-----------|---------|----------|
| `assets/templates/` | Content generation templates | `x-single.md`, `foundation-chapter.md` |
| `assets/chapter-templates/` | Book chapter structure templates | `job-story-chapter.md`, `meta-chapter.md` |
| `references/` | Configuration and guides | `config.md`, `voice-guide.md`, `api-guide.md` |
| `scripts/` | Python CLI utilities | `format_session.py`, `validate_post.py` |

---

## File Naming Conventions

### Markdown Files

- **General content:** `lowercase-hyphen-separated.md`
  - Examples: `voice-guide.md`, `session-template.md`, `book-structure.md`

- **Date-stamped content:** `YYYY-MM-DD-slug.md`
  - Examples: `2026-01-05-api-refactor.md`, `2026-01-03-deploy-fix.md`

- **Chapter files:** `chapter-XX-descriptive-title.md`
  - Examples: `chapter-01-getting-started.md`, `chapter-07-debugging-patterns.md`

- **Templates:** `platform-format.md` or `chapter-type.md`
  - Examples: `x-single.md`, `linkedin.md`, `foundation-chapter.md`

### Python Scripts

- **Naming:** `descriptive_verb_noun.py`
  - Examples: `format_session.py`, `validate_post.py`, `bitbucket_api.py`

- **Executable:** All scripts have execute permissions (`chmod +x`)

- **Shebang:** `#!/usr/bin/env python3`

### Configuration

- **Always named:** `config.md` (located in `references/` directory)
- **Contains:** Example configurations with placeholder values
- **Security:** NEVER commit with real credentials, tokens, or passwords

---

## Python Scripts Reference

### format_session.py (code-journey-documenter)

Transforms raw session logs into structured chapter drafts.

```bash
# Basic usage: Convert session log to chapter draft
python code-journey-documenter/scripts/format_session.py session-2026-01-02.md > chapter-draft.md

# Extract only tagged moments ([INSIGHT], [FAILURE], [PATTERN], [META])
python code-journey-documenter/scripts/format_session.py --tags-only session.md

# Help
python code-journey-documenter/scripts/format_session.py --help
```

**What it does:**
- Extracts YAML frontmatter metadata (date, project, chapter, challenge)
- Parses tagged moments: `[INSIGHT]`, `[FAILURE]`, `[PATTERN]`, `[META]`
- Extracts prompt/response pairs from conversation logs
- Generates structured output with sections:
  - Opening Hook (The Problem)
  - Approach
  - Iterations
  - What Went Wrong
  - The Breakthrough
  - The Pattern
  - Reader Exercise

**Exit codes:** 0 = success, 1 = error

---

### validate_post.py (social-media-poster)

Validates social media posts for platform compliance before publishing.

```bash
# Validate a post
python social-media-poster/scripts/validate_post.py post.md

# Exit codes: 0 = ready to post, 1 = has issues
```

**What it checks:**

| Platform | Checks |
|----------|--------|
| **X/Twitter** | Character limit (280), hashtag usage (discouraged), engagement bait, clichés |
| **LinkedIn** | Character limit (3,000), hashtag count (3-5 optimal), paragraph structure |
| **Both** | Frontmatter validity, voice consistency, opening hooks |

**Visual feedback:**
- ✓ (green check) = Passes validation
- ⚠️ (yellow warning) = Minor issues, review recommended
- ❌ (red X) = Critical issues, fix required

**Exit codes:**
- `0` = Ready to post
- `1` = Has issues

---

### bitbucket_api.py (bitbucket-repo-lookup)

**IMPORTANT: Bitbucket Server vs Cloud Support**

This script supports **both** Bitbucket Cloud and Bitbucket Server/Data Center instances with automatic detection based on the base URL.

| Instance Type | API Base URL Pattern | Detection |
|--------------|---------------------|-----------|
| **Cloud** | `https://api.bitbucket.org/2.0` | Default, or `api.bitbucket.org` in URL |
| **Server/Data Center** | `https://your-domain.com/rest/api/1.0` | Contains `/rest/api` or custom domain |

**Auto-detection:** The script automatically detects the instance type from the `BITBUCKET_BASE_URL` environment variable or `--base-url` argument.

Bitbucket Cloud REST API v2.0 wrapper for repository discovery and cloning.

**Requires external dependency:** `pip install requests`

```bash
# List all repositories
python bitbucket-repo-lookup/scripts/bitbucket_api.py list

# Search with filters
python bitbucket-repo-lookup/scripts/bitbucket_api.py search --project backend --language python

# Filter by name
python bitbucket-repo-lookup/scripts/bitbucket_api.py search --name api

# Filter by recent activity (updated in last 30 days)
python bitbucket-repo-lookup/scripts/bitbucket_api.py search --updated-within 30

# Combined filters
python bitbucket-repo-lookup/scripts/bitbucket_api.py search --project backend --language python --updated-within 30

# Clone repositories
python bitbucket-repo-lookup/scripts/bitbucket_api.py clone repo-slug
python bitbucket-repo-lookup/scripts/bitbucket_api.py clone repo-slug-1 repo-slug-2 repo-slug-3

# Clone all from search results
python bitbucket-repo-lookup/scripts/bitbucket_api.py search --project backend --clone-all

# Repository info
python bitbucket-repo-lookup/scripts/bitbucket_api.py info repo-slug
```

**Authentication methods:**
1. App password (recommended): `username` + `app_password` in config.md
2. Access token: `access_token` in config.md
3. Environment variables: `BITBUCKET_USERNAME`, `BITBUCKET_APP_PASSWORD`, or `BITBUCKET_ACCESS_TOKEN`

**API Details:**
- Pagination: Default 50 per page, max 100
- Retry logic: 3 attempts with 2-second delays
- Clone methods: HTTPS or SSH
- Supports shallow clones: `--depth N`

---

## bitbucket-repo-lookup Implementation Details

**Critical for future development and debugging.**

### Credential Auto-Loading (2026-01-06)

The script implements **automatic credential loading** from `.credentials` file - no manual sourcing required!

**Three-tier credential resolution** (priority order):
1. **CLI arguments** (`--username`, `--password`, `--base-url`)
2. **Environment variables** (`BITBUCKET_USERNAME`, `BITBUCKET_APP_PASSWORD`, `BITBUCKET_BASE_URL`)
3. **`.credentials` file** (auto-parsed from multiple locations)

**Auto-discovery locations:**
```python
# Searches in order:
1. bitbucket-repo-lookup/references/.credentials  # Skill location
2. ./references/.credentials                       # Current directory
3. ./.credentials                                  # Current directory
```

**File format:** Bash export statements
```bash
export BITBUCKET_USERNAME="your-username"
export BITBUCKET_APP_PASSWORD="your-token-or-app-password"
export BITBUCKET_BASE_URL="https://bitbucket.example.com/rest/api/1.0"
```

**Implementation:** Uses regex parsing (`r'^export\s+([A-Z_]+)="([^"]*)"'`) to extract credentials without executing shell commands.

**Security:** `.credentials` file is in `.gitignore` and should have `600` permissions (owner read/write only).

### Argument Parser Pattern (Fixed 2026-01-06)

**CRITICAL:** All subcommands must inherit from `parent_parser` to access credential arguments.

```python
# Define parent parser with common arguments (lines 537-540)
parent_parser = argparse.ArgumentParser(add_help=False)
parent_parser.add_argument("--base-url", help="Bitbucket base URL")
parent_parser.add_argument("--username", help="Bitbucket username")
parent_parser.add_argument("--password", help="Bitbucket app password/access token")

# Subcommands MUST include parents=[parent_parser]
list_parser = subparsers.add_parser("list", parents=[parent_parser])    # ✓ Correct
info_parser = subparsers.add_parser("info", parents=[parent_parser])    # ✓ Correct
clone_parser = subparsers.add_parser("clone", parents=[parent_parser])  # ✓ Correct
```

**Why:** Without `parents=[parent_parser]`, subcommands can't access `args.username`, `args.password`, or `args.base_url`, causing `AttributeError: 'Namespace' object has no attribute 'username'`.

### Bitbucket Server vs Cloud API Differences

**Endpoint Structures:**

| Operation | Cloud API | Server API |
|-----------|-----------|------------|
| **List repos** | `/repositories/{workspace}` | `/projects/{project}/repos` |
| **Get repo** | `/repositories/{workspace}/{repo}` | `/projects/{project}/repos/{repo}` |
| **Get commits** | `/repositories/{workspace}/{repo}/commits` | `/projects/{project}/repos/{repo}/commits` |

**Response Format Differences:**

| Field | Cloud | Server |
|-------|-------|--------|
| **Commit ID** | `hash` | `id` |
| **Author** | `author.user.display_name` | `author.displayName` |
| **Timestamp** | `date` | `authorTimestamp` |
| **Pagination param** | `pagelen` | `limit` |
| **Clone URLs** | `links.clone[].href` | `links.clone[].href` (same) |

**Implementation Pattern:**

```python
def method(self, workspace: str, repo_slug: str):
    is_server = hasattr(self, 'is_server') and self.is_server

    if is_server:
        # Bitbucket Server logic
        url = f"{self.base_url}/projects/{workspace}/repos/{repo_slug}"
        data = self._make_request("GET", url)
        return Repository.from_server_response(data, workspace)
    else:
        # Bitbucket Cloud logic
        url = f"{self.base_url}/repositories/{workspace}/{repo_slug}"
        data = self._make_request("GET", url)
        return Repository.from_api_response(data)
```

**Methods with dual support:**
- `list_repositories()` (lines 205-322)
- `get_repository()` (lines 324-346)
- `get_latest_commit()` (lines 348-392)

### URL Encoding for Credentials (Fixed 2026-01-06)

**CRITICAL:** API tokens often contain special characters (especially `/`) that must be properly URL-encoded when embedding in clone URLs.

**Problem:** Default `quote()` doesn't encode `/` characters, causing git to misinterpret credentials.

**Solution:** Use `quote(value, safe='')` to encode ALL special characters:

```python
# WRONG - doesn't encode '/' in passwords
clone_url = f"https://{quote(username)}:{quote(password)}@{domain}/repo.git"

# CORRECT - encodes all special characters including '/'
clone_url = f"https://{quote(username, safe='')}:{quote(password, safe='')}@{domain}/repo.git"
```

**Example:**
```python
# Example token with special characters: "abc123/def456+xyz789"
quote(token)           # abc123/def456+xyz789  ❌ '/' and '+' not encoded
quote(token, safe='')  # abc123%2Fdef456%2Bxyz789  ✓ '/' → %2F, '+' → %2B
```

**Location:** `clone_repository()` method, lines 420-424

### Error Messages and Debugging

**Common errors and their causes:**

| Error | Cause | Fix |
|-------|-------|-----|
| `AttributeError: 'Namespace' object has no attribute 'username'` | Subparser missing `parents=[parent_parser]` | Add `parents=[parent_parser]` to subparser definition |
| `Authentication failed` | Wrong API endpoint (Cloud vs Server) | Set `BITBUCKET_BASE_URL` correctly for your instance |
| `Resource not found` | Wrong API endpoint format | Check if using Server endpoints with Cloud credentials or vice versa |
| `URL rejected: Port number was not a decimal number` | Special chars in password not URL-encoded | Use `quote(password, safe='')` instead of `quote(password)` |
| `Missing credentials error` | `.credentials` file not found or malformed | Verify file exists and uses correct format |

### Testing Checklist

When modifying `bitbucket_api.py`, test all three commands:

```bash
# Test with credentials from .credentials file (no env vars set)
unset BITBUCKET_USERNAME BITBUCKET_APP_PASSWORD BITBUCKET_BASE_URL

# 1. List command
python3 bitbucket-repo-lookup/scripts/bitbucket_api.py list --workspace PROJECT --limit 3

# 2. Info command
python3 bitbucket-repo-lookup/scripts/bitbucket_api.py info --workspace PROJECT --repo REPO_SLUG

# 3. Clone command
python3 bitbucket-repo-lookup/scripts/bitbucket_api.py clone --workspace PROJECT --repos REPO_SLUG --dest /tmp/test
```

**Expected results:**
- All commands load credentials automatically
- Server instances show correct project/repo info
- Clone succeeds with credentials properly embedded in URL

---

## Configuration Patterns

### Critical Security Rules

**⚠️ NEVER commit credentials to version control**

- Credentials stored separately from configuration
- `.credentials` file is in `.gitignore` (never committed)
- Use `.credentials.example` as template (safe to commit)
- Rotate tokens regularly
- Use app passwords (more secure than account passwords, can be revoked)

### Credential Management (bitbucket-repo-lookup)

**Three-tier authentication strategy:**

1. **Environment variables (recommended)**:
   - `BITBUCKET_USERNAME`, `BITBUCKET_APP_PASSWORD`
   - Most secure, works across sessions
   - Add to `~/.bashrc` or `~/.zshrc`

2. **Local .credentials file**:
   - Copy from `.credentials.example`, source before use
   - Convenient for project-specific credentials
   - Already in `.gitignore`

3. **CLI arguments**:
   - For one-off operations only
   - Not recommended for regular use

**Files:**
- `.credentials.example` - Template (checked in, safe)
- `.credentials` - Your actual credentials (in .gitignore, NOT checked in)
- `config.md` - Non-sensitive configuration only (workspace, paths, preferences)

**Setup:**
```bash
# Copy template
cp bitbucket-repo-lookup/references/.credentials.example bitbucket-repo-lookup/references/.credentials

# Edit with your values
# Then source before using
source bitbucket-repo-lookup/references/.credentials
```

### Skill Orchestration Patterns

When a skill depends on another skill's functionality, use the **Dependencies/Workflow pattern** rather than explicit "automatic" or "manual" invocation instructions.

**Pattern Structure:**

```markdown
## Dependencies

| Skill | Path | Purpose |
|-------|------|---------|
| skill-name | `path/to/SKILL.md` | Brief description of what it provides |

## Workflow

### 1. Step Name
- Read skill-name skill
- Perform action using skill functionality
- Alternative options if applicable
```

**Example: credential-setup orchestration**

```markdown
## Dependencies

| Skill | Path | Purpose |
|-------|------|---------|
| credential-setup | `credential-setup/SKILL.md` | Configure API credentials |

## Workflow

### 1. Authenticate
- Read credential-setup skill
- Ensure .credentials exists for service access
- Alternative: Use environment variables or CLI args
```

**Benefits:**
- **Declarative** - Dependencies listed upfront in table
- **Workflow-driven** - Integration happens naturally in workflow steps
- **Consistent** - Same pattern across all skill orchestrations
- **No implementation details** - Doesn't prescribe how Claude invokes dependencies
- **Single path** - No "automatic vs manual" dichotomy

**Reference Implementation:** See `bitbucket-repo-lookup/SKILL.md` for complete example.

**Anti-patterns to avoid:**
- ❌ "Claude will automatically detect and invoke..."
- ❌ "If X doesn't exist, this skill will automatically..."
- ❌ Separate "Automatic (Recommended)" and "Manual" sections
- ❌ Prerequisites section with setup instructions

### Configuration Loading

All skills use `references/config.md` for non-sensitive configuration:

```yaml
# Example structure (YAML-style key: value format)
workspace: your-workspace-slug
username: your-username
app_password: your-app-password-here

clone:
  base_directory: ~/repos
  method: https
  organize_by_project: true
```

**Path expansion:**
- `~` expands to home directory
- Relative paths resolved from config file location
- Absolute paths used as-is

### Common Configuration Keys

| Category | Keys | Example Values |
|----------|------|----------------|
| **Paths** | `book_path`, `posts_path`, `clone/base_directory` | `~/dev/personal/books/code-with-claude` |
| **Auth** | `username`, `app_password`, `access_token` | `david@example.com`, `app_password_token_here` |
| **Filters** | `language`, `project`, `updated_within_days` | `python`, `backend`, `30` |
| **Output** | `verbose`, `show_progress`, `confirm_bulk_clone` | `true`, `true`, `true` |

---

## Content Conventions

### YAML Frontmatter Pattern

All content files (SKILL.md, templates, posts) use YAML frontmatter:

```yaml
---
name: skill-name
description: "Brief description of purpose and use cases"
platform: x | x-thread | linkedin
status: draft | ready | posted
created: YYYY-MM-DD
---
```

### Session Log Tags (code-journey-documenter)

Use these tags to mark important moments during coding sessions:

| Tag | Purpose | Example |
|-----|---------|---------|
| `[INSIGHT]` | Key learning moments, things that clicked | `[INSIGHT] The race condition only happens when...` |
| `[FAILURE]` | What didn't work and why | `[FAILURE] This approach failed because...` |
| `[PATTERN]` | Transferable techniques worth teaching | `[PATTERN] Always validate API responses before...` |
| `[META]` | Reflections on the process itself | `[META] Using AI for debugging changed my workflow...` |

### Post Status Workflow (social-media-poster)

Posts follow this lifecycle:

```
draft → ready → posted
```

- **draft:** Work in progress, not validated
- **ready:** Validated, scheduled for publishing
- **posted:** Published to platform (includes `posted: YYYY-MM-DD` in frontmatter)

### Post Frontmatter

```yaml
---
platform: x | x-thread | linkedin
status: draft | ready | posted
created: 2026-01-02
posted: 2026-01-03            # Only when status = posted
session_source: path/to/source-session.md  # Optional
tags: [claude-code, debugging, api]        # For organization, not hashtags
---
```

---

## Code Style and Quality Standards

### Python

- **Version:** Python 3.x required
- **CLI parsing:** Use `argparse` for command-line interfaces
- **File paths:** Use `pathlib.Path` for cross-platform compatibility
- **Parsing:** Regular expressions for pattern matching
- **Exit codes:**
  - `0` = success
  - `1` = error or validation failure
- **Docstrings:** Include module docstring with usage examples
- **Error handling:** Graceful failures with helpful error messages

**Example CLI pattern:**
```python
#!/usr/bin/env python3
"""
Script description here.

Usage:
    python script.py input.md
    python script.py --flag input.md
"""
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="Script description")
    parser.add_argument("file", type=Path, help="Input file")
    args = parser.parse_args()
    # ... implementation

if __name__ == "__main__":
    main()
```

### Markdown

- **Flavor:** GitHub-flavored markdown
- **Code blocks:** Always specify language (```python, ```bash, ```yaml)
- **Tables:** Use for structured data
- **Headers:** Clear section hierarchy (# → ## → ###)
- **Lists:** Consistent bullet style (- or *)

### Voice (social-media-poster)

Five core principles for authentic technical writing:

1. **Practitioner, not pundit** - Write as someone who builds, not comments
   - Good: "Spent 3 hours on this bug. Here's what I learned."
   - Bad: "Developers should really pay more attention to error handling."

2. **Specific over general** - Concrete details beat abstractions
   - Good: "Reduced build time from 4 min to 23 sec by switching to esbuild."
   - Bad: "Optimizing your build pipeline can really improve DX."

3. **Humble confidence** - Share without excessive hedging or overclaiming
   - Good: "This approach worked for my use case. YMMV."
   - Bad: "I'm no expert, but maybe this could possibly help someone..."

4. **Show the work** - Journey is more interesting than destination
   - Include what you tried that didn't work
   - The moment something clicked
   - The specific trigger that led to insight

5. **Conversational technical** - Technical accuracy with accessible language
   - Good: "The race condition happened because both handlers fired before the state updated."
   - Bad: "There was a concurrency issue in the asynchronous event propagation layer."

---

## Important Gotchas

### When Editing Skills

1. **SKILL.md frontmatter must be valid YAML**
   - Syntax errors break skill loading
   - Use quotes for multi-line descriptions
   - Test: `python -c "import yaml; yaml.safe_load(open('SKILL.md').read().split('---')[1])"`

2. **Template placeholders use brackets:** `[TEXT IN BRACKETS]`
   - Don't use `{{var}}` or `<placeholder>`
   - Be descriptive: `[Brief description of the problem]` not `[Problem]`

3. **Python scripts must be executable**
   - Run: `chmod +x scripts/*.py`
   - Verify shebang: `#!/usr/bin/env python3`

4. **Config.md is user-specific - don't overwrite**
   - Check before editing
   - Preserve user's credentials and paths
   - Add new keys, don't replace entire file

### When Adding New Skills

1. **Follow directory pattern:**
   ```
   [skill-name]/
   ├── SKILL.md
   ├── assets/templates/
   ├── references/
   │   └── config.md
   └── scripts/
   ```

2. **Include config.md with examples**
   - Provide complete example configuration
   - Use placeholder values (never real credentials)
   - Document all available options

3. **Add to README.md skills table**
   - Update "Skills at a Glance" section
   - Add detailed documentation section
   - Include in project structure tree

4. **Document in appropriate voice**
   - Professional but accessible
   - Include usage examples
   - Explain the "why" not just the "how"

### Platform-Specific Rules

| Platform | Character Limit | Hashtags | Special Rules |
|----------|-----------------|----------|---------------|
| **X/Twitter** | 280 | NO (discouraged) | No engagement bait, no clichés |
| **X/Twitter Thread** | 280 per tweet | NO | Number tweets (1/, 2/, 3/...) |
| **LinkedIn** | 3,000 | 3-5 optimal | Professional tone, use paragraphs |

**Book chapters must include:**
- Opening hook (real-world problem)
- The attempt (approach with tools)
- The struggle (iterations, failures)
- The breakthrough (what worked and why)
- The pattern (generalizable principle)
- Reader exercise (try-it-yourself with success criteria)

### Dependencies

- **code-journey-documenter:** Python standard library only
- **social-media-poster:** Python standard library only
- **bitbucket-repo-lookup:** Requires `requests` library
  - Install: `pip install requests`
  - Import fails gracefully with helpful error message

---

## No Build/Test Infrastructure

This repository intentionally has **no build system or automated tests**:

- ❌ No `package.json` or `requirements.txt`
- ❌ No automated test suite
- ❌ No CI/CD pipeline configuration
- ❌ No Makefile or build scripts

**Why?** Scripts are standalone executables meant to be run directly. Each skill is self-contained.

### To Use This Repository

1. **Clone repository**
   ```bash
   git clone https://github.com/My-Partner-Source/claude-code-skills.git
   ```

2. **Install Python 3.x** (if not already installed)
   ```bash
   python3 --version  # Should be 3.7 or higher
   ```

3. **(Optional) Install dependencies for bitbucket-repo-lookup**
   ```bash
   pip install requests
   ```

4. **Configure each skill**
   - Edit `[skill-name]/references/config.md`
   - Replace placeholders with your values
   - NEVER commit real credentials

5. **Run scripts directly**
   ```bash
   python code-journey-documenter/scripts/format_session.py session.md
   python social-media-poster/scripts/validate_post.py post.md
   python bitbucket-repo-lookup/scripts/bitbucket_api.py list
   ```

---

## Git Workflow

### Branch Strategy

- **Main branch:** `main`
- **Feature branches:** `feature/descriptive-name` or `skill-name/improvement`
- **Bug fixes:** `fix/issue-description`

### Commit Messages

Follow conventional commits style:

```
feat(skill-name): Add new feature
fix(skill-name): Fix bug description
docs(skill-name): Update documentation
refactor(skill-name): Refactor code
chore: Update dependencies
```

**Examples:**
- `feat(code-journey): Add chapter summary extraction`
- `fix(social-media): Correct character count for threads`
- `docs(bitbucket): Update authentication guide`

### Author Information

- **Author:** David Rutgos
- **Email:** david.rutgos@gmail.com
- **License:** MIT (Copyright 2026 My Partner Source)
- **Repository:** https://github.com/My-Partner-Source/claude-code-skills

---

## Contributing

When contributing to this repository:

1. **Maintain consistency**
   - Follow existing directory patterns
   - Use established naming conventions
   - Preserve voice and tone in documentation

2. **Security first**
   - Never commit credentials
   - Use placeholders in examples
   - Document security best practices

3. **Document thoroughly**
   - Update README.md for user-facing changes
   - Update AGENTS.md for structural changes
   - Include usage examples in docstrings

4. **Test manually**
   - Run scripts with various inputs
   - Verify error handling
   - Check exit codes

5. **Keep it simple**
   - Prefer standalone scripts over frameworks
   - Minimize dependencies
   - Write clear, readable code

---

## Quick Reference

### Common Tasks

| Task | Command |
|------|---------|
| Format session log | `python code-journey-documenter/scripts/format_session.py session.md > chapter.md` |
| Validate social post | `python social-media-poster/scripts/validate_post.py post.md` |
| List Bitbucket repos | `python bitbucket-repo-lookup/scripts/bitbucket_api.py list` |
| Clone repo | `python bitbucket-repo-lookup/scripts/bitbucket_api.py clone repo-name` |

### Configuration Files

| Skill | Config Location | Purpose |
|-------|----------------|---------|
| code-journey-documenter | `references/config.md` | Book repository path |
| social-media-poster | `references/config.md` | Posts repository structure |
| bitbucket-repo-lookup | `references/config.md` | Workspace, clone settings (credentials in `.credentials`) |

### Important Files

| File | Purpose |
|------|---------|
| `SKILL.md` | Skill definition and metadata |
| `config.md` | User-specific configuration |
| `voice-guide.md` | Writing tone and style rules |
| `book-structure.md` | Complete book outline |
| `api-guide.md` | Bitbucket API reference |

---

**Last Updated:** 2026-01-06
**Version:** 1.1.0
**Maintained by:** David Rutgos

**Recent Changes (2026-01-06):**
- Added comprehensive bitbucket-repo-lookup implementation details
- Documented Bitbucket Server vs Cloud API differences
- Documented credential auto-loading mechanism
- Documented parent_parser pattern for argparse subcommands
- Documented URL encoding requirements for credentials in clone URLs
- Added common errors and debugging guide
- Added testing checklist for bitbucket_api.py modifications
