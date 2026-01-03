# Pattern Library

Collected patterns from documented sessions. Each pattern follows the format:
- **Name**: Memorable identifier
- **Problem**: When you'd use this
- **Solution**: The technique
- **Example**: Concrete prompt or workflow
- **Source**: Session where discovered

---

## Prompting Patterns

### The Constraint Sandwich
**Problem:** Claude Code goes off-track with open-ended prompts
**Solution:** Bracket your request with constraints before and after
**Example:**
```
Only modify files in src/utils/. 
Refactor the date handling functions to use day.js instead of moment.
Do not change any function signatures or add new dependencies.
```
**Source:** [Session date when discovered]

### The Explicit Non-Goal
**Problem:** Claude Code adds "helpful" features you didn't ask for
**Solution:** State what NOT to do alongside what to do
**Example:**
```
Add input validation to the user registration form.
Do NOT add any UI changes, error styling, or toast notifications.
```
**Source:** [Session date]

### The Checkpoint Prompt
**Problem:** Long tasks where you lose track of progress
**Solution:** Ask Claude Code to summarize before continuing
**Example:**
```
Before making the next change, summarize what you've modified so far 
and what remains to be done.
```
**Source:** [Session date]

---

## Workflow Patterns

### Explore Before You Commit
**Problem:** Jumping into code changes without understanding context
**Solution:** Always start with exploration prompts
**Example:**
```
Before making changes, explain:
1. How the current authentication flow works
2. Which files are involved
3. What would break if we modify the session handling
```
**Source:** [Session date]

### The Test-First Constraint
**Problem:** Claude Code makes changes that break existing behavior
**Solution:** Require tests to pass as part of the task
**Example:**
```
Refactor the payment processor. After each change, run the test suite.
Do not proceed if any tests fail.
```
**Source:** [Session date]

### Staged Rollout
**Problem:** Large changes are hard to review
**Solution:** Break work into explicit, committable stages
**Example:**
```
Let's do this in stages:
Stage 1: Add the new database schema (commit when done)
Stage 2: Create the migration script (commit when done)
Stage 3: Update the API endpoints (commit when done)
Tell me when each stage is complete so I can review.
```
**Source:** [Session date]

---

## Debugging Patterns

### The Rubber Duck Escalation
**Problem:** Claude Code's first explanation isn't clear enough
**Solution:** Ask for progressively simpler explanations
**Example:**
```
Explain this bug.
[response]
Explain it simpler, as if I've never seen this codebase.
[response]
Now explain what's happening at the byte level.
```
**Source:** [Session date]

### The Hypothesis Test
**Problem:** Uncertain about root cause
**Solution:** Have Claude Code generate and test hypotheses explicitly
**Example:**
```
The API returns 500 intermittently. Generate 3 hypotheses for the cause,
then for each hypothesis, tell me what evidence would confirm or rule it out.
```
**Source:** [Session date]

---

## Documentation Patterns

### The Future Reader Prompt
**Problem:** Documentation that's too terse or too verbose
**Solution:** Specify the reader's context
**Example:**
```
Document this function for a developer who:
- Knows Python but not this codebase
- Will be debugging this at 2am during an outage
- Needs to understand the failure modes
```
**Source:** [Session date]

### The Commit Message Narrative
**Problem:** Commit messages that don't tell the story
**Solution:** Ask for context-rich commit messages
**Example:**
```
Write a commit message that explains:
1. What changed (the what)
2. Why it changed (the business reason)
3. How to verify it works (the test)
```
**Source:** [Session date]

---

## Anti-Patterns (What NOT to Do)

### The Kitchen Sink Prompt
**Problem:** Asking for too much in one prompt
**Symptom:** Claude Code produces incomplete or confused output
**Fix:** Break into smaller, focused prompts

### The Ambiguous "Fix It"
**Problem:** Vague prompts like "fix the bug" or "make it work"
**Symptom:** Claude Code guesses at what you mean, often wrong
**Fix:** Specify the expected behavior and current behavior

### The Trust Fall
**Problem:** Letting Claude Code make changes without review
**Symptom:** Subtle bugs introduced, context lost
**Fix:** Review diffs before committing, use staged rollout pattern

---

## Template: Adding New Patterns

When you discover a new pattern during a session:

```markdown
### [Pattern Name]
**Problem:** [When you'd use this]
**Solution:** [The technique in one sentence]
**Example:**
\`\`\`
[Concrete prompt or workflow]
\`\`\`
**Source:** Session [date] - [project name]
```

Add patterns as you discover them. This library becomes Appendix B.
