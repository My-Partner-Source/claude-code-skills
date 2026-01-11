---
name: code-journey-documenter
version: 1.0.0
description: "Document coding sessions and learnings for the book 'Code With Claude: How AI Transformed the Way I Work (And Think).' Use this skill when (1) recording a coding session for a book chapter, (2) transforming raw session logs into narrative content, (3) capturing iterations, failures, and breakthroughs during Claude Code work, (4) generating chapter outlines from job experiences, or (5) creating meta-reflections on the book-writing process itself."
---

# Code Journey Documenter

Transform coding sessions into book-ready content for "Code With Claude: How AI Transformed the Way I Work (And Think)."

## Core Philosophy

Document mastery through three lenses:
1. **Doing** — Actual coding work with Claude Code
2. **Reflecting** — What worked, failed, surprised
3. **Teaching** — Distillable patterns for readers

## Workflow: Session to Chapter

### Step 1: Pre-Session Setup

Before starting a coding task for documentation, establish:
- Job/project name and technical challenge
- Target chapter (see references/book-structure.md)
- Learning objectives for this session

### Step 2: During-Session Capture

While working, capture:
- **Prompts** — Exact wording given to Claude Code
- **Responses** — Especially unexpected ones
- **Iterations** — What you refined and why
- **Failures** — Mark with [FAILURE] tag
- **Insights** — Mark with [INSIGHT] tag

Use format in references/session-template.md.

### Step 3: Post-Session Processing

Transform raw logs into narrative:
1. Run `scripts/format_session.py` on raw log
2. Identify story arc: challenge → approach → iteration → resolution
3. Draft using assets/chapter-templates/
4. Tag transferable techniques with [PATTERN]

### Step 4: Integration

Map session to book structure:
- **Part I (Foundations)** — Setup, first encounters, mental models
- **Part II (Real-World Mastery)** — Job stories, one chapter per project
- **Part III (Beyond)** — Meta-reflections, advanced patterns

See references/book-structure.md for chapter mapping.

## Session Log Format

```markdown
## Session: [DATE] - [PROJECT_NAME]

### Context
- Chapter target: [Chapter X: Title]
- Challenge: [One-line description]

### Prompts & Iterations
1. Initial prompt: "[exact prompt]"
   - Response: [summary]
   - Outcome: [worked/partial/failed]
   
2. Refined prompt: "[adjusted prompt]"
   - Changes: [what you adjusted]
   - Outcome: [result]

### Key Moments
- [INSIGHT] [realization]
- [FAILURE] [what went wrong]
- [PATTERN] [transferable technique]

### Reflection
- What I'd do differently
- Teaching angle for readers
- Connection to mastery journey
```

## Chapter Draft Structure

1. **Opening Hook** — Real-world problem, vivid terms
2. **The Attempt** — Approach with Claude Code
3. **The Struggle** — Iterations, failures, pivots
4. **The Breakthrough** — What worked and why
5. **The Pattern** — Generalizable principle
6. **Reader Exercise** — Try-it-yourself prompt

## Meta-Documentation

Tag recursive moments with [META]:
- When Claude Code helps write about itself
- When the tool fails at documenting the tool
- Insights about AI-assisted authorship

## Reference Files

- **references/config.md** — Book repository path and directory mapping (READ THIS FIRST)
- **references/book-structure.md** — Complete book outline
- **references/session-template.md** — Detailed logging format
- **references/pattern-library.md** — Collected patterns from sessions
