# Social Media Posts Configuration

## Posts Repository Location

posts_path: ~/dev/personal/social-posts

## Directory Structure

```
{posts_path}/
├── x/
│   ├── drafts/           # Work in progress
│   ├── ready/            # Ready to post
│   ├── posted/           # Archive of posted content
│   └── threads/
│       ├── drafts/
│       ├── ready/
│       └── posted/
├── linkedin/
│   ├── drafts/
│   ├── ready/
│   └── posted/
└── ideas.md              # Parking lot for future post ideas
```

## File Naming

- Single posts: `YYYY-MM-DD-brief-slug.md`
- Threads: `YYYY-MM-DD-brief-slug.md` (all tweets in one file)

## Workflow States

Posts move through directories based on status:
1. Create in `drafts/`
2. Move to `ready/` when approved
3. Move to `posted/` after publishing (update frontmatter with posted date)

## Integration with Book Repository

When generating posts from book sessions, reference the source:

```yaml
---
session_source: ~/dev/personal/books/code-with-claude/session-logs/2025-01-02-auth-refactor.md
---
```

This creates traceability between deep work and social content.
