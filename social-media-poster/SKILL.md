---
name: social-media-poster
version: 1.0.0
description: "Generate dev log social media posts from coding sessions. Use this skill when (1) creating X/Twitter posts or threads about development work, (2) writing LinkedIn posts about technical learnings, (3) converting session logs or book content into social content, or (4) building a queue of posts for scheduled publishing."
---

# Social Media Poster

Generate developer-focused social media content from coding sessions, book chapters, or standalone insights.

## Core Philosophy

Posts should feel like a smart colleague sharing genuine learnings—not marketing. The goal is to document the journey publicly, building an audience through authenticity and useful insights.

Voice: See references/voice-guide.md for style guidelines.

## Supported Platforms

| Platform | Format | Character Limit | Hashtags |
|----------|--------|-----------------|----------|
| X/Twitter | Single post | 280 | No (discouraged) |
| X/Twitter | Thread | 280 per tweet | No |
| LinkedIn | Post | 3,000 | Yes (2-5 max) |

## Workflow: Session to Post

### Step 1: Identify the Hook

Every post needs a hook—the single insight that makes someone stop scrolling.

From a coding session, look for:
- A surprising discovery
- A mistake that taught something
- A before/after transformation
- A counterintuitive result
- A tool or technique worth sharing

### Step 2: Choose Platform & Format

**X Single Post** — One atomic insight, punchy delivery
**X Thread** — A narrative with multiple beats, numbered or connected
**LinkedIn** — Deeper reflection, professional framing, can include context

See references/platform-x.md and references/platform-linkedin.md for platform rules.

### Step 3: Draft Using Templates

Use templates in assets/templates/ for each format.

### Step 4: Save to Posts Repository

Check references/config.md for repository path. Save posts as:
- `x/YYYY-MM-DD-slug.md` — Single X posts
- `x/threads/YYYY-MM-DD-slug.md` — X threads  
- `linkedin/YYYY-MM-DD-slug.md` — LinkedIn posts

Include frontmatter with status and metadata.

## Post Frontmatter Format

```yaml
---
platform: x | x-thread | linkedin
status: draft | ready | posted
created: YYYY-MM-DD
posted: YYYY-MM-DD (when published)
session_source: (optional) path to source session log
tags: [topic1, topic2] (for your organization, not hashtags)
---
```

## Quick Reference

### X Single Post Structure
```
[Hook - the insight in <200 chars]

[Optional: one supporting detail]

[Optional: call to engagement - question or invitation]
```

### X Thread Structure
```
1/ [Hook - why should I read this thread?]

2/ [Context - the setup]

3/ [The meat - what happened]

4/ [The insight - what I learned]

5/ [The takeaway - what you can apply]
```

### LinkedIn Structure
```
[Hook line - pattern interrupt]

[Empty line]

[2-3 paragraphs of substance]

[Empty line]

[Takeaway or question]

[Empty line]

[2-5 hashtags]
```

## Reference Files

- **references/config.md** — Posts repository path (READ THIS FIRST)
- **references/platform-x.md** — X/Twitter best practices and constraints
- **references/platform-linkedin.md** — LinkedIn best practices
- **references/voice-guide.md** — Writing style and tone guidelines
