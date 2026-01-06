# Usage Guide for Skill Developers

How to integrate credential-setup into your skills for automatic credential management.

## Quick Integration (3 Steps)

### 1. Create `.credentials.example`

Place in `your-skill/references/.credentials.example`:

```bash
# [Your Skill Name] Credentials
# Copy to .credentials and fill in your actual values
# DO NOT commit .credentials - it's in .gitignore

# Primary method (recommended)
export API_KEY="your-api-key-here"
export API_URL="https://api.example.com"

# Alternative: OAuth
# export OAUTH_TOKEN="your-oauth-token-here"
```

### 2. Declare Dependency in SKILL.md

Add Dependencies section and integrate into workflow:

```markdown
## Dependencies

| Skill | Path | Purpose |
|-------|------|---------|
| credential-setup | `credential-setup/SKILL.md` | Configure [Your Service] credentials |

## Workflow

### 1. Authenticate
- Read credential-setup skill
- Ensure .credentials exists for [Service] access
```

### 3. Test

```bash
# Remove .credentials to test
rm your-skill/references/.credentials

# Run your skill - should trigger automatic setup
```

## Complete Example: bitbucket-repo-lookup

See `bitbucket-repo-lookup/` for a working implementation.

## Best Practices

1. **Use descriptive variable names** - `BITBUCKET_USERNAME` not `USER`
2. **Group related credentials** - Use comments to show options
3. **Mark optional credentials** - Comment out with `#`
4. **Provide hints** - Use meaningful placeholder values
5. **Document in SKILL.md** - Explain what credentials are needed

## Testing Checklist

- [ ] `.credentials.example` exists in references/
- [ ] Placeholders are helpful (not just "value")
- [ ] Comments explain each credential group
- [ ] SKILL.md mentions automatic setup
- [ ] Manual command is documented
- [ ] Tested with actual setup
