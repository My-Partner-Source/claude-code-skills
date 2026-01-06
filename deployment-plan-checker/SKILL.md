---
name: deployment-plan-checker
description: Check deployment plans on Atlassian Confluence to verify team members have completed their Bamboo entries. Use when user asks to check/review/audit a deployment plan URL, verify team deployment readiness, or check completeness for QA/UAT/PROD environments.
version: 1.0.0
---

# Deployment Plan Checker

Check deployment plans on Confluence to verify team Bamboo entry completeness.

## Prerequisites

- **VPN connected** — Run `/vpn-check` first (required to access yourcompany.atlassian.net)
- **Atlassian MCP** must be configured and authenticated
- **Team config** must exist at `references/.team-config`
- **Credentials** must exist at `references/.credentials` with cloudId

### Stacked Skills

This skill depends on:
- **vpn-check** — Verifies VPN connectivity before attempting Atlassian access
- **credential-setup** — Helps create `.credentials` from template

### First-Time Setup

If `references/.credentials` doesn't exist, invoke the `credential-setup` skill:
```
/credential-setup
```

If `references/.team-config` doesn't exist:
```bash
cd ~/.claude/skills/deployment-plan-checker/references
cp .team-config.example .team-config
# Edit with your team member names (one per line)
```

---

## Workflow

### Step 0: Verify VPN Connectivity

Before accessing Atlassian, verify VPN is connected:

```
/vpn-check
```

Or programmatically:
```bash
python ~/.claude/skills/vpn-check/scripts/check_vpn.py --quiet
# Exit code 0 = connected, 1 = not connected
```

If VPN is not connected, stop and inform user to connect before proceeding.

### Step 1: Load Configuration

Read configuration files:

```bash
# Load team members
cat ~/.claude/skills/deployment-plan-checker/references/.team-config

# Load credentials (for cloudId)
cat ~/.claude/skills/deployment-plan-checker/references/.credentials
```

Parse team members into a list (ignore lines starting with `#`).
Extract `ATLASSIAN_CLOUD_ID` from credentials.

If either file is missing, stop and guide user through setup.

### Step 2: Parse URL and Extract Page ID

From the user-provided URL or search term, extract the page ID:

**URL patterns:**
- Full URL: `https://yourcompany.atlassian.net/wiki/spaces/FD/pages/123456789/Title` → pageId: `123456789`
- Tiny URL: `https://yourcompany.atlassian.net/wiki/x/AbCdEf` → needs resolution via search
- Page ID only: `123456789` → use directly
- Search term: `"QA20260107"` → search Confluence

**URL extraction regex:**
```
/pages/(\d+)  →  capture group 1 is pageId
```

### Step 3: Fetch Confluence Page

Use Atlassian MCP to retrieve page content. Verified tool names:

**To find cloudId (first time only):**
```
mcp__atlassian__getAccessibleAtlassianResources()
# Returns list of accessible Atlassian sites with their UUIDs
```

**To fetch a page by ID:**
```
mcp__atlassian__getConfluencePage({
  cloudId: "<uuid-from-credentials>",
  pageId: "<extracted-page-id>",
  contentFormat: "markdown"
})
```

**To search for a page:**
```
mcp__atlassian__search({
  query: "<search-term>"
})
```

If authentication fails (error about cloudId not granted), prompt user to:
1. Run `/mcp` in Claude Code
2. Clear and re-authenticate to Atlassian
3. Select the correct Atlassian site during OAuth

### Step 4: Parse Release Highlights

From the page content, locate the **"Release Highlights - All Products"** section.

This is a table with columns:
| Type | Key | Summary | Assignee | Priority | Status | Updated |

**Extract rows where Assignee matches a team member from config.**

Store as `teamItems[]`:
```json
[
  {"key": "PROJ-1234", "summary": "Feature description", "assignee": "John Smith", "status": "DEPLOYMENT READY"}
]
```

### Step 5: Parse Bamboos Section

Locate the **"Bamboos"** section containing deployment entries.

Table columns:
| Engineering Lead | DevOps | Component / Service | Build Link | Config Changes | Health Checks | Dependencies | Jira Item(s) | Rollback Link |

**Important:** Team member names appear as `@Name` mentions in the markdown output. Search for team members by looking for their names after `@` symbols or in `<custom data-type="mention">` tags.

For each team member from config, find their Bamboo entries by searching the "Engineering Lead" column.

### Step 6: Check Completeness

A Bamboo entry is **COMPLETE** when ALL required columns have values:

| Column | Required Value |
|--------|----------------|
| Engineering Lead | Any name (not empty) |
| DevOps | "DevOps" or a name |
| Component / Service | Component name |
| Build Link | URL or build reference with env/build info |
| Config Changes | Y, N, or New |
| Health Checks | URL or N/A |
| Dependencies | N or dependency list |
| Jira Item(s) | Jira key (e.g., PROJ-1234) |
| Rollback Link | URL |

**Classify each entry:**
- **Complete**: All required columns filled
- **Incomplete**: One or more required columns empty/missing
- **Missing**: Jira item in Release Highlights but no Bamboo entry

### Step 7: Generate Report

Output a structured report:

```markdown
## Deployment Plan Check: [Environment] [Date]

**Page**: [Confluence URL]
**Checked**: [timestamp]

### Team Items in Release Highlights
| Jira | Summary | Assignee | Status |
|------|---------|----------|--------|
| PROJ-1234 | Feature description | John Smith | DEPLOYMENT READY |

### Bamboo Entry Status

#### Complete Entries
| # | Lead | Component | Jira |
|---|------|-----------|------|
| 1 | John Smith | service-name | PROJ-1234 |

#### Incomplete Entries (Action Required)
| # | Lead | Component | Jira | Missing Fields |
|---|------|-----------|------|----------------|
| 5 | Jane Doe | other-service | PROJ-5678 | Build Link, Rollback Link |

#### Missing Bamboo Entries
Items in Release Highlights with no corresponding Bamboo entry:
- PROJ-9999: "Another feature" (Assignee: Bob)

### Summary
- Team items in Release Highlights: X
- Complete Bamboo entries: Y/X
- Incomplete Bamboo entries: Z
- Missing Bamboo entries: W
- **Status: READY** or **NOT READY (Z incomplete, W missing)**
```

---

## Edge Cases

| Case | Handling |
|------|----------|
| Auth expired | Detect MCP error, prompt user to re-auth via browser |
| Page not found | Clear error with URL, suggest searching |
| No team items | Report "No items found for configured team members" |
| Jira in highlights but not in Bamboos | Flag in "Missing Bamboo Entries" |
| Multiple leads on one entry | Match if ANY team member in Engineering Lead |
| Empty deployment plan | Handle gracefully, note page may be incomplete |

---

## Example Usage

```
User: Check the deployment plan at https://yourcompany.atlassian.net/wiki/spaces/FD/pages/123456789/QA-Deployment

Claude: [Loads config, extracts pageId 123456789, fetches page, parses tables, generates report]
```

```
User: Is my team ready for the QA20260107 deployment?

Claude: [Searches for "QA20260107", finds page, checks team's Bamboo entries]
```
