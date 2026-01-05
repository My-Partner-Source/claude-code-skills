# Claude Code Skills

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A collection of Claude Code skills to streamline your development workflow: document your coding journey, share insights authentically, and manage Bitbucket repositories directly from Claude Code.

## Skills at a Glance

| Skill | Description | Invoke with |
|-------|-------------|-------------|
| [code-journey-documenter](#code-journey-documenter) | Transform sessions into book chapters | `/code-journey-documenter` |
| [social-media-poster](#social-media-poster) | Convert insights into social posts | `/social-media-poster` |
| [bitbucket-repo-lookup](#bitbucket-repo-lookup) | List and clone Bitbucket repositories | `/bitbucket-repo-lookup` |

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

1. **Configure Authentication**
   - Edit `bitbucket-repo-lookup/references/config.md` with your Bitbucket credentials
   - Set workspace slug, app password, and default clone directory

2. **List Repositories**
   ```
   "List all repositories in my Bitbucket workspace"
   "Show me repos in the 'backend' project"
   "Find repositories containing 'api' in the name"
   ```

3. **Clone Repositories**
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

- **Never commit credentials** — Keep `config.md` in `.gitignore` if sharing
- **Use App Passwords** — More secure than account passwords, can be revoked
- **Minimal permissions** — Only request repository read access (sufficient for listing and cloning repositories)
- **Token rotation** — Regularly rotate your access tokens

See `bitbucket-repo-lookup/SKILL.md` for complete documentation.

---

## Configuration

Each skill has its own configuration file. Edit the `references/config.md` file in each skill directory to customize paths and settings.

### Default Paths

| Skill | Output Directory |
|-------|------------------|
| code-journey-documenter | `~/dev/personal/books/code-with-claude` |
| social-media-poster | `~/dev/personal/social-posts` |
| bitbucket-repo-lookup | `~/repos` (clone destination) |

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
└── bitbucket-repo-lookup/
    ├── SKILL.md                          # Skill definition
    ├── assets/
    │   └── templates/
    │       ├── repo-list.md              # Repository listing template
    │       └── clone-summary.md          # Clone summary template
    ├── references/
    │   ├── config.md                     # Path and auth configuration
    │   └── api-guide.md                  # Bitbucket API reference
    └── scripts/
        └── bitbucket_api.py              # API helper script
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
