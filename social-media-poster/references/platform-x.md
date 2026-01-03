# X (Twitter) Platform Guidelines

## Hard Constraints

- **Character limit**: 280 characters per tweet
- **Thread limit**: No hard limit, but 5-10 tweets is optimal
- **Links**: Shortened, count as ~23 characters regardless of length
- **Images**: Up to 4 per tweet, don't count against character limit

## Platform Culture (2024-2025)

### No Hashtags

Per platform guidance, hashtags are discouraged on X. They:
- Look spammy and dated
- Don't significantly boost discovery anymore
- Break reading flow
- Signal "trying too hard"

**Instead**: Write naturally. The algorithm surfaces content based on engagement and relevance, not hashtag matching.

### What Performs Well

- **Hot takes** with substance behind them
- **Contrarian views** that are defensible
- **Specific numbers** and concrete results
- **Before/after** comparisons
- **Failures** shared honestly
- **Tools and techniques** that saved time
- **Code snippets** (as images or inline)
- **Questions** that invite genuine discussion

### What Doesn't Work

- Vague inspirational content ("Work hard, dream big")
- Obvious statements everyone agrees with
- Engagement bait ("Like if you agree!")
- Excessive self-promotion
- Walls of text without line breaks
- Corporate/marketing voice

## Single Post Best Practices

### Structure

```
[Hook - 1 sentence, <200 chars ideally]

[Supporting detail OR space]

[Optional: question or invitation to engage]
```

### Examples

**Good:**
```
Spent 3 hours debugging a race condition.

Claude Code found it in 45 seconds by asking "what happens if the user double-clicks?"

The AI didn't write the fix. It asked the question I forgot to ask.
```

**Bad:**
```
Just used AI to help with coding and it was really helpful! Everyone should try using AI assistants for their development work. #coding #AI #developer #programming
```

## Thread Best Practices

### When to Thread

- Story with multiple beats
- Tutorial or walkthrough
- List of related insights
- Complex topic needing context

### Structure

```
1/ [Hook - why read this thread?]
   Make it self-contained. Many see only tweet 1.

2/ [Setup - context needed]
   What problem? What situation?

3-N/ [The meat]
   One idea per tweet
   Each should stand somewhat alone
   Use "↓" or numbering to signal continuation

Last/ [Takeaway]
   What should reader remember?
   Optional: question to drive replies
```

### Thread Mechanics

- Number tweets (1/, 2/, 3/ or 1/10, 2/10, etc.)
- First tweet must hook—most people won't click "Show thread"
- Each tweet should be valuable alone (people quote-tweet individual parts)
- End with something memorable or actionable

### Examples

**Good thread opener:**
```
1/ I mass-applied to 400 companies in 2019 and got 3 responses.

Last month, I mass-applied to 15 and got 11 interviews.

Here's what changed (it's not AI): 🧵
```

**Bad thread opener:**
```
1/ Thread on my thoughts about the current state of software development and how things have changed over the years 🧵
```

## Code in Tweets

### Options

1. **Inline code**: Use backticks for short snippets (renders as monospace)
2. **Screenshots**: For syntax highlighting and longer code
3. **Carbon.now.sh**: For beautiful code images
4. **Ray.so**: Alternative code screenshot tool

### Best Practices

- Keep code snippets under 10 lines for screenshots
- Ensure font size is readable on mobile
- Remove unnecessary code—show only the relevant part
- Add a brief explanation before or after

## Engagement Patterns

### Reply Strategy

When your post gets engagement:
- Reply to substantive comments (boosts visibility)
- Don't reply to every "Great post!"
- Add additional context in self-replies if needed

### Timing

- Dev Twitter is global—no perfect time
- Consistency matters more than optimization
- Threads: post in morning (your timezone) for max initial engagement

## Don'ts

- Never delete and repost for better engagement (looks desperate)
- Don't tag people hoping for retweets
- Don't start with "I" (pattern interrupt is better)
- Don't use more than 1-2 emojis
- Don't ask for retweets/likes explicitly
