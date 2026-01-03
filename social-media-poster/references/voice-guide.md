# Voice & Style Guide

This guide defines the writing voice for social posts—authentic, technical, and insight-driven.

## Core Voice Principles

### 1. Practitioner, Not Pundit

Write as someone who builds things, not someone who comments on people who build things.

**Good:** "Spent 3 hours on this bug. Here's what I learned."
**Bad:** "Developers should really pay more attention to error handling."

### 2. Specific Over General

Concrete details beat abstract principles. Numbers, names, and specifics create credibility.

**Good:** "Reduced build time from 4 min to 23 sec by switching to esbuild."
**Bad:** "Optimizing your build pipeline can really improve DX."

### 3. Humble Confidence

Share what you learned without hedging excessively or overclaiming.

**Good:** "This approach worked for my use case. YMMV."
**Bad:** "I'm no expert, but maybe this could possibly help someone..."
**Also bad:** "This is the definitive way to handle auth in 2025."

### 4. Show the Work

The journey is more interesting than the destination. Include:
- What you tried that didn't work
- The moment something clicked
- The specific trigger that led to insight

### 5. Conversational Technical

Technical accuracy with accessible language. Assume smart readers who may not know your specific domain.

**Good:** "The race condition happened because both handlers fired before the state updated."
**Bad:** "There was a concurrency issue in the asynchronous event propagation layer."
**Also bad:** "The code was doing things in the wrong order."

## Tone Calibration

| Avoid | Aim For |
|-------|---------|
| "Amazing!" "Incredible!" | "Useful." "Interesting." |
| "You should definitely..." | "This worked for me..." |
| "Everyone needs to..." | "If you're dealing with X, try Y" |
| "I'm so excited to share..." | [Just share it] |
| "Quick thread 🧵" | [Just start the thread] |

## Sentence Patterns

### Strong Openers

- Start with the insight, not the setup
- Avoid "I" as first word (pattern interrupt works better)
- Use tension or surprise

**Examples:**
- "45 seconds. That's how long Claude Code took to find a bug I'd missed for 3 hours."
- "The best debugging technique isn't a technique. It's a question."
- "Shipped on Friday. Broke on Saturday. Here's why I'd do it again."

### Useful Patterns

**The Contrast:**
"Before: [old approach]. After: [new approach]. The difference: [insight]."

**The Counter-intuitive:**
"[Common belief]. Except when [specific exception]. Here's what I found."

**The Admission:**
"I was mass-applying to jobs thinking it was a numbers game. It wasn't."

**The Specific Number:**
"[Specific number] [thing]. That's [context]. Here's why."

## Things to Avoid

### Clichés

- "Game-changer"
- "10x developer"
- "Crushing it"
- "Let's gooo"
- "This."
- "Thread 🧵" (just number your tweets)

### Empty Phrases

- "In today's fast-paced world..."
- "It goes without saying..."
- "At the end of the day..."
- "To be honest..." (implies you're usually dishonest)

### Hedging

- "I feel like maybe..."
- "I'm not sure but..."
- "This might not work for everyone but..."

(One caveat is fine. Excessive hedging kills credibility.)

### Hype

- "Revolutionary"
- "Mind-blowing"
- "You won't believe..."
- "The secret to..."

## Emoji Usage

### X/Twitter
- 0-2 emojis max per post
- Never in thread numbering (use 1/, 2/, not 1️⃣, 2️⃣)
- OK for visual breaks in threads
- Never multiple emojis in a row

### LinkedIn
- 0-3 emojis acceptable
- Can use as bullet points sparingly
- More acceptable in hooks
- Still avoid emoji spam

## Code Sharing

When sharing code:
- Show only the relevant part (10 lines max)
- Add brief context before
- Explain what to notice
- Credit sources if not original

**Example:**
```
Found this pattern in the codebase. Elegant way to handle the race condition:

[code screenshot]

The key: the closure captures the current state before the async call.
```

## Self-Promotion Guidelines

### Acceptable
- Sharing what you built and what you learned building it
- Mentioning your book/project when directly relevant
- Celebrating genuine milestones

### Not Acceptable
- "Check out my new [thing]!" without substance
- Every post linking to your product
- Humble-bragging ("So humbled that 10,000 people downloaded...")

**Rule of thumb:** If you removed the self-promotional element, would the post still be valuable? If not, don't post it.

## The "Boris Test"

Before posting, ask:
1. Is there a genuine insight here?
2. Would I find this useful if someone else posted it?
3. Am I showing the work, not just the result?
4. Is this specific enough to be actionable?
5. Does it sound like a practitioner, not a marketer?

If yes to all five, ship it.
