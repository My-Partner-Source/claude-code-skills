# Project Instructions for Claude

## First Action: Read AGENTS.md

**CRITICAL:** Before working on this codebase, you MUST read the AGENTS.md file in the project root:

```
Read: AGENTS.md
```

This file contains:
- Complete codebase structure and conventions
- Technical implementation details for all skills
- Common errors and debugging guides
- Configuration patterns and security rules
- Recent changes and version history

## Project Overview

This is the **claude-code-skills** repository - a collection of three specialized skills:
1. `code-journey-documenter` - Transform coding sessions into book chapters
2. `social-media-poster` - Convert insights into X/Twitter and LinkedIn posts
3. `bitbucket-repo-lookup` - Discover, search, and clone Bitbucket repositories

## Package Manager

**Always use `pnpm` instead of `npm`** for any Node.js operations (though this is primarily a Python project).

## Git Workflow

**Always use worktrees** when implementing new features or fixing bugs:

```bash
# Create worktree for new feature
git worktree add -b feature/descriptive-name ../feature-descriptive-name

# Create worktree for bug fix
git worktree add -b fix/issue-description ../fix-issue-description
```

## Critical Security Rule

**NEVER commit credentials to version control:**
- `.credentials` files are in `.gitignore`
- Use `.credentials.example` as templates
- Only commit placeholder values in config files
- Rotate tokens regularly

## Important Files

| File | Purpose |
|------|---------|
| `AGENTS.md` | Complete codebase documentation (READ THIS FIRST) |
| `README.md` | User-facing documentation |
| `[skill]/SKILL.md` | Individual skill definitions |
| `[skill]/references/config.md` | Non-sensitive configuration |
| `[skill]/references/.credentials` | Actual credentials (gitignored, NOT committed) |

## When Working on bitbucket-repo-lookup

**Read the Implementation Details section in AGENTS.md** (lines 279-433) before making changes.

Critical areas:
- Bitbucket Server vs Cloud support (auto-detected)
- Credential auto-loading from `.credentials` file
- Parent parser pattern for argparse subcommands
- URL encoding for credentials (`safe=''` parameter required)

**Always test all three commands** after changes:
```bash
python3 bitbucket-repo-lookup/scripts/bitbucket_api.py list --workspace PROJECT --limit 3
python3 bitbucket-repo-lookup/scripts/bitbucket_api.py info --workspace PROJECT --repo REPO
python3 bitbucket-repo-lookup/scripts/bitbucket_api.py clone --workspace PROJECT --repos REPO
```

---

**Repository:** https://github.com/My-Partner-Source/claude-code-skills
**Author:** David Rutgos
**License:** MIT
**Last Updated:** 2026-01-06
