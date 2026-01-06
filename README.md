# Claude Code Skills

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A collection of Claude Code skills to streamline your development workflow: document your coding journey, share insights authentically, and manage Bitbucket repositories directly from Claude Code.

## Skills at a Glance

| Skill | Description | Invoke with |
|-------|-------------|-------------|
| [code-journey-documenter](#code-journey-documenter) | Transform sessions into book chapters | `/code-journey-documenter` |
| [social-media-poster](#social-media-poster) | Convert insights into social posts | `/social-media-poster` |
| [bitbucket-repo-lookup](#bitbucket-repo-lookup) | List and clone Bitbucket repositories | `/bitbucket-repo-lookup` |
| [vpn-check](#vpn-check) | Verify VPN connectivity before internal access | `/vpn-check` |
| [credential-setup](#credential-setup) | Interactive credential configuration helper | `/credential-setup` |
| [deployment-plan-checker](#deployment-plan-checker) | Verify team Bamboo entries in deployment plans | `/deployment-plan-checker` |

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/My-Partner-Source/claude-code-skills.git
   ```

2. Add to your Claude Code skills directory:
   ```bash
   # Option 1: Symlink (recommended for development)
   ln -s /path/to/claude-code-skills ~/.claude/skills/claude-code-skills

   # Option 2: Copy
   cp -r /path/to/claude-code-skills ~/.claude/skills/
   ```

3. Skills are now available in Claude Code via their slash commands.

---

## Code Journey Documenter

Transform coding sessions into book-ready content for "Code With Claude: How AI Transformed the Way I Work (And Think)."

### Core Philosophy

Document mastery through three lenses:
1. **Doing** — Actual coding work with Claude Code
2. **Reflecting** — What worked, failed, surprised
3. **Teaching** — Distillable patterns for readers

### Session Tags

Tag moments during your coding sessions for later processing:

| Tag | Purpose |
|-----|---------|
| `[INSIGHT]` | Key learning moments—things that clicked |
| `[FAILURE]` | What didn't work and why |
| `[PATTERN]` | Recurring strategies worth teaching |
| `[META]` | Reflections on the process itself |

### Workflow

```
1. Pre-Session    → Define job, chapter target, learning objectives
        ↓
2. During-Session → Capture prompts, responses, iterations with tags
        ↓
3. Post-Session   → Run format_session.py to generate chapter draft
        ↓
4. Integration    → Map to book structure and expand
```

### Chapter Draft Structure

Every chapter follows this arc:
1. **Opening Hook** — Real-world problem in vivid terms
2. **The Attempt** — Your approach with Claude Code
3. **The Struggle** — Iterations, failures, pivots
4. **The Breakthrough** — What worked and why
5. **The Pattern** — Generalizable principle
6. **Reader Exercise** — Try-it-yourself prompt

### Script Usage

```bash
# Convert a session log into a chapter draft
python code-journey-documenter/scripts/format_session.py session-2026-01-02.md > chapter-draft.md
```

The script extracts metadata, prompts, iterations, and tagged moments to generate a structured chapter draft.

### Book Structure

The book follows three parts:
- **Part I: Foundations** — Setup, first encounters, mental models
- **Part II: Real-World Mastery** — Job stories, one chapter per project
- **Part III: Beyond** — Meta-reflections, advanced patterns

See `code-journey-documenter/references/book-structure.md` for the complete outline.

---

## Social Media Poster

Generate developer-focused social media content from coding sessions, book chapters, or standalone insights.

### Core Philosophy

> Posts should feel like a smart colleague sharing genuine learnings—not marketing.

The goal is to document the journey publicly, building an audience through authenticity and useful insights.

### Supported Platforms

| Platform | Format | Character Limit | Hashtags |
|----------|--------|-----------------|----------|
| X/Twitter | Single post | 280 | No (discouraged) |
| X/Twitter | Thread | 280 per tweet | No |
| LinkedIn | Post | 3,000 | Yes (2-5 max) |

### Voice Principles

The voice guide emphasizes authenticity over marketing:

1. **Practitioner, Not Pundit** — Write as someone who builds things
2. **Specific Over General** — Concrete details beat abstract principles
3. **Humble Confidence** — Share without excessive hedging or overclaiming
4. **Show the Work** — The journey is more interesting than the destination
5. **Conversational Technical** — Technical accuracy with accessible language

#### Examples

| Avoid | Aim For |
|-------|---------|
| "Developers should really pay more attention to error handling." | "Spent 3 hours on this bug. Here's what I learned." |
| "Optimizing your build pipeline can really improve DX." | "Reduced build time from 4 min to 23 sec by switching to esbuild." |

### Validation Script

```bash
# Validate a post before publishing
python social-media-poster/scripts/validate_post.py post.md
```

The validator checks:
- Platform-specific character limits
- Hashtag compliance (LinkedIn yes, X no)
- Cliché and engagement bait detection
- Voice consistency with the style guide

### Post Frontmatter

```yaml
---
platform: x | x-thread | linkedin
status: draft | ready | posted
created: 2026-01-02
posted: 2026-01-03
session_source: path/to/source-session.md
tags: [claude-code, debugging]
---
```

---

## Bitbucket Repo Lookup

Look up, list, and clone repositories from Bitbucket workspaces without leaving Claude Code.

### Core Philosophy

Bridge the gap between your Bitbucket cloud workspace and local development environment. Instead of manually browsing Bitbucket's web interface, use this skill to discover, search, and clone repositories with natural language commands.

### Workflow

```
1. Authenticate → Set credentials in config.md
        ↓
2. List/Search → Query workspace repos with filters
        ↓
3. Select      → Pick from list or specify "all"
        ↓
4. Clone       → Download to local directory
```

### Quick Start

1. **Set Up Credentials**
   ```bash
   # Copy the credentials template
   cp bitbucket-repo-lookup/references/.credentials.example bitbucket-repo-lookup/references/.credentials

   # Edit .credentials with your Bitbucket credentials
   # Source before using
   source bitbucket-repo-lookup/references/.credentials
   ```

2. **Configure Workspace**
   - Edit `bitbucket-repo-lookup/references/config.md` to set workspace slug and clone directory

3. **List Repositories**
   ```
   "List all repositories in my Bitbucket workspace"
   "Show me repos in the 'backend' project"
   "Find repositories containing 'api' in the name"
   ```

4. **Clone Repositories**
   ```
   "Clone repos 1, 3, and 5"
   "Download all of them"
   "Clone the 'user-service' repository"
   ```

### Filtering Options

| Filter | Example |
|--------|---------|
| By project | "List repos in the 'backend' project" |
| By language | "Show only Python repositories" |
| By name | "Find repos containing 'service'" |
| By activity | "List repos updated in the last 30 days" |
| Combined | "Python repos in backend updated this month" |

### Security Notes

- **Credentials stored separately** — Use `.credentials` file (not checked in) or environment variables
- **Never commit credentials** — `.credentials` is in `.gitignore` to prevent accidental commits
- **Template provided** — Copy `.credentials.example` to `.credentials` and fill in your values
- **Use App Passwords** — More secure than account passwords, can be revoked independently
- **Minimal permissions** — Only request repository read access (sufficient for listing and cloning)
- **Token rotation** — Regularly rotate your access tokens for security

See `bitbucket-repo-lookup/SKILL.md` for complete documentation.

---

## VPN Check

Verify VPN connectivity by checking if internal hostnames can be resolved via DNS. Use standalone or as a prerequisite for skills requiring internal network access.

### Core Philosophy

Fast, reliable VPN detection without requiring authentication or service availability. DNS resolution is the simplest indicator of network connectivity.

### Quick Start

```bash
# First run prompts for configuration
python vpn-check/scripts/check_vpn.py

# After setup, check status
python vpn-check/scripts/check_vpn.py

# Quiet mode for scripting
python vpn-check/scripts/check_vpn.py --quiet
```

### Configuration

On first run, the skill prompts for:
- **Internal hostname** — A hostname only resolvable when on VPN
- **Expected IP** (optional) — For extra validation

Configuration is stored at `~/.claude/skills/vpn-check/.vpn-config` (never committed to git).

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | VPN connected |
| 1 | VPN not connected |
| 2 | Configuration error |

### Skill Stacking

Other skills can use vpn-check as a prerequisite. For example, `bitbucket-repo-lookup` automatically checks VPN status before accessing Bitbucket Server instances.

See `vpn-check/SKILL.md` for complete documentation.

---

## Credential Setup

Interactive helper for setting up credentials from `.credentials.example` templates.

### Core Philosophy

Security through separation: Credentials should never be committed to version control. This skill helps users create `.credentials` files from templates through interactive prompts.

### Quick Start

```bash
# Set up credentials for a skill
python credential-setup/scripts/setup_credentials.py --skill bitbucket-repo-lookup

# Preview without creating
python credential-setup/scripts/setup_credentials.py --skill bitbucket-repo-lookup --dry-run
```

### What It Does

1. Locates `.credentials.example` for the specified skill
2. Parses bash `export` statements to identify required variables
3. Prompts interactively for each credential (with password masking)
4. Creates `.credentials` file with proper permissions (600)
5. Validates against `.gitignore` patterns

### Integration

Skills requiring credentials declare `credential-setup` as a dependency and include a `.credentials.example` template.

See `credential-setup/SKILL.md` for complete documentation.

---

## Deployment Plan Checker

Check FUSE EVV deployment plans on Atlassian Confluence to verify team members have completed their Bamboo entries.

### Core Philosophy

Automate the tedious process of checking deployment readiness. Instead of manually scanning Confluence pages for your team's entries, let Claude parse the tables and generate a status report.

### Quick Start

1. **Verify VPN Connection** (required):
   ```
   /vpn-check
   ```
   Must be on VPN to access hhaxsupport.atlassian.net

2. **Configure Atlassian MCP** (required):
   - Run `/mcp` in Claude Code
   - Authenticate with your Atlassian account
   - Ensure you select the correct Atlassian site during OAuth

3. **Set Up Team Config**:
   ```bash
   cd ~/.claude/skills/deployment-plan-checker/references
   cp .team-config.example .team-config
   # Edit with team member names (one per line)
   ```

4. **Set Up Credentials**:
   ```bash
   cp .credentials.example .credentials
   # Edit with your Atlassian cloudId (UUID format)
   # Find cloudId via: mcp__atlassian__getAccessibleAtlassianResources()
   ```

5. **Check a Deployment Plan**:
   ```
   "Check the deployment plan at https://hhaxsupport.atlassian.net/wiki/spaces/FD/pages/..."
   "Is my team ready for the QA20260107 deployment?"
   ```

### What It Checks

For each team member in your config, the skill:

1. **Finds their entries** in the "Bamboos" section
2. **Validates completeness** of required fields:
   - Engineering Lead, DevOps, Component/Service
   - Build Link (with env/build info)
   - Config Changes (Y/N/New)
   - Health Checks, Dependencies, Jira Items, Rollback Link
3. **Generates a report** with complete/incomplete/missing entries

### Report Output

```markdown
## Deployment Plan Check: QA20260107 (Jan 7, 2026)

### Bamboo Entry Status
#### ✅ Complete Entries
| Lead | Component | Jira |
|------|-----------|------|
| John Lu | intake-visit-gateway | SPD-6156 |

#### ❌ Incomplete Entries (Action Required)
| Lead | Component | Jira | Missing Fields |
|------|-----------|------|----------------|
| Jane Doe | other-service | SPD-5678 | Build Link, Rollback Link |

### Summary
- **Status: ✅ READY** or **❌ NOT READY**
```

See `deployment-plan-checker/SKILL.md` for complete documentation.

---

## Configuration

Each skill has its own configuration file. Edit the `references/config.md` file in each skill directory to customize paths and settings.

### Default Paths

| Skill | Output Directory |
|-------|------------------|
| code-journey-documenter | `~/dev/personal/books/code-with-claude` |
| social-media-poster | `~/dev/personal/social-posts` |
| bitbucket-repo-lookup | `~/repos` (clone destination) |
| vpn-check | `~/.claude/skills/vpn-check/.vpn-config` |
| credential-setup | Creates `.credentials` in skill's `references/` directory |
| deployment-plan-checker | `~/.claude/skills/deployment-plan-checker/references/` |

### Directory Structure (Book)

```
~/dev/personal/books/code-with-claude/
├── chapters/
│   ├── part-1/
│   ├── part-2/
│   └── part-3/
├── sessions/          # Raw session logs
├── code-examples/     # Referenced code snippets
├── drafts/            # Work in progress
└── assets/            # Images, diagrams
```

### Directory Structure (Social Posts)

```
~/dev/personal/social-posts/
├── x/
│   ├── drafts/
│   ├── ready/
│   ├── posted/
│   └── threads/
└── linkedin/
    ├── drafts/
    ├── ready/
    └── posted/
```

---

## Project Structure

```
claude-code-skills/
├── README.md
├── AGENTS.md                             # AI assistant context
├── LICENSE
├── .gitignore
│
├── code-journey-documenter/
│   ├── SKILL.md                          # Skill definition
│   ├── assets/
│   │   └── chapter-templates/
│   │       ├── foundation-chapter.md     # Part I template
│   │       ├── job-story-chapter.md      # Part II template
│   │       └── meta-chapter.md           # Part III template
│   ├── references/
│   │   ├── config.md                     # Path configuration
│   │   ├── book-structure.md             # Complete book outline
│   │   ├── pattern-library.md            # Collected patterns
│   │   └── session-template.md           # Session logging format
│   └── scripts/
│       └── format_session.py             # Session → Chapter converter
│
├── social-media-poster/
│   ├── SKILL.md                          # Skill definition
│   ├── assets/
│   │   └── templates/
│   │       ├── x-single.md               # Single tweet template
│   │       ├── x-thread.md               # Thread template
│   │       └── linkedin.md               # LinkedIn post template
│   ├── references/
│   │   ├── config.md                     # Path configuration
│   │   ├── platform-x.md                 # X/Twitter best practices
│   │   ├── platform-linkedin.md          # LinkedIn best practices
│   │   └── voice-guide.md                # Writing style guide
│   └── scripts/
│       └── validate_post.py              # Post validator
│
├── bitbucket-repo-lookup/
│   ├── SKILL.md                          # Skill definition
│   ├── assets/
│   │   └── templates/
│   │       ├── repo-list.md              # Repository listing template
│   │       └── clone-summary.md          # Clone summary template
│   ├── references/
│   │   ├── config.md                     # Path and auth configuration
│   │   ├── api-guide.md                  # Bitbucket API reference
│   │   └── .credentials.example          # Credentials template
│   └── scripts/
│       └── bitbucket_api.py              # API helper script
│
├── vpn-check/
│   ├── SKILL.md                          # Skill definition
│   ├── references/
│   │   └── .vpn-config.example           # Configuration template
│   └── scripts/
│       └── check_vpn.py                  # VPN connectivity checker
│
├── credential-setup/
│   ├── SKILL.md                          # Skill definition
│   ├── references/
│   │   └── usage-guide.md                # Integration guide
│   └── scripts/
│       └── setup_credentials.py          # Interactive credential setup
│
└── deployment-plan-checker/
    ├── SKILL.md                          # Skill definition
    └── references/
        ├── .team-config.example          # Team member template
        ├── .credentials.example          # Atlassian cloudId template
        └── .gitignore                    # Protects credentials
```

---

## Author

**David Rutgos**
- Email: [david.rutgos@gmail.com](mailto:david.rutgos@gmail.com)
- LinkedIn: [linkedin.com/in/davidrutgos](https://www.linkedin.com/in/davidrutgos/)
- X: [@DavidRutgos](https://x.com/DavidRutgos)

---

## Contributing

Contributions are welcome! If you have ideas for improving these skills or want to share your own Claude Code workflows:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/improvement`)
3. Commit your changes (`git commit -am 'Add improvement'`)
4. Push to the branch (`git push origin feature/improvement`)
5. Open a Pull Request

---

## License

MIT License - see [LICENSE](LICENSE) for details.

Copyright (c) 2026 My Partner Source
