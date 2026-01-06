---
name: deployment-plan-checker
description: Check deployment plans on Atlassian Confluence to verify team members have completed their Bamboo entries. Use when user asks to check/review/audit a deployment plan URL, verify team deployment readiness, or check completeness for QA/UAT/PROD environments.
version: 1.2.0
---

# Deployment Plan Checker

Check deployment plans on Confluence to verify team Bamboo entry completeness.

## Key Behavior

**IMPORTANT: This skill ONLY reports on team members defined in `.team-config`.**

- Filter OUT all other team members (Hiren, Benjamin, Michael, etc.) from reports
- Only show entries where Engineering Lead matches a configured team member
- When a section is empty, that means configured team members have NO entries (not ready)

## Environment Comparison Logic

### Deployment Plan Hierarchy
```
QA (source) → UAT (mirrors QA) → PROD (mirrors UAT)
```

**There is no DEV plan.** QA is the starting point.

### Comparison Rules

| Checking | Compare Against | If Empty/Incomplete |
|----------|-----------------|---------------------|
| **PROD** | UAT | Fetch UAT, show missing entries |
| **UAT** | QA | Fetch QA, show missing entries |
| **QA** | (none) | QA is the source — report as-is |

### PROD Plans
- **PROD should mirror UAT** — All entries from UAT should be copied to PROD
- **Empty sections = NOT READY** — If MySQL Scripts or Bamboo Items are empty but UAT has entries, PROD is incomplete

### UAT Plans
- **UAT should mirror QA** — All entries from QA should be copied to UAT
- **Empty sections = NOT READY** — If MySQL Scripts or Bamboo Items are empty but QA has entries, UAT is incomplete

### QA Plans
- **QA is the source** — No upstream comparison needed
- Report team entries as complete/incomplete based on field validation only

### Version Requests (e.g., "check EVV 8.52")
1. Search for the PROD deployment plan for that version
2. If PROD sections are empty, also fetch UAT to show expected entries
3. Report what's missing from PROD compared to UAT

## Prerequisites

- **VPN connected** — Run `/vpn-check` first
- **Atlassian MCP** must be configured and authenticated
- **Team config** must exist at `references/.team-config`
- **Credentials** must exist at `references/.credentials` with cloudId

### Stacked Skills

- **vpn-check** — Verifies VPN connectivity before Atlassian access
- **credential-setup** — Helps create `.credentials` from template

---

## Workflow

### Step 0: Verify VPN Connectivity

```
/vpn-check
```

Or: `python ~/.claude/skills/vpn-check/scripts/check_vpn.py --quiet`

### Step 1: Load Configuration

```bash
cat ~/.claude/skills/deployment-plan-checker/references/.team-config
cat ~/.claude/skills/deployment-plan-checker/references/.credentials
```

Parse team members into a list (ignore `#` comments).
**These are the ONLY people to include in reports.**

### Step 2: Identify Target Plan

From user request, determine:
- **Specific URL** → Extract pageId directly
- **Version number** (e.g., "EVV 8.52") → Search for PROD plan first
- **Environment + date** (e.g., "QA20260107") → Search for that specific plan

**Search priority for version requests:**
1. PROD plan for that version
2. If PROD empty, also fetch UAT for comparison

### Step 3: Fetch Confluence Page(s)

```
mcp__atlassian__getConfluencePage({
  cloudId: "<uuid-from-credentials>",
  pageId: "<page-id>",
  contentFormat: "markdown"
})
```

```
mcp__atlassian__search({
  query: "<version> PROD deployment"
})
```

### Step 4: Parse Sections (Team Members Only)

Scan these sections for **configured team members only**:

1. **MySQL Scripts** — Look for team names in "Engineering Lead" column
2. **Bamboo Items** — Look for team names in "Engineering Lead" column
3. **Oracle Items** — Look for team names in "Engineering Lead" column

**Filtering rule:** Only include rows where Engineering Lead contains a name from `.team-config`

### Step 5: Check Completeness

For each team member entry found:

| Column | Required |
|--------|----------|
| Engineering Lead | Team member name |
| DevOps/DBOps | "DevOps", "DBOps", or name |
| Component/Service or File Name | Not empty |
| Build Link (Bamboo) or File Name (MySQL) | URL or path |
| Jira Item(s) | Jira key |
| Rollback Link | URL or N/A |

### Step 6: Compare Against Upstream (if applicable)

**For PROD plans** — If sections are empty/incomplete:
1. Fetch corresponding UAT plan for the same version
2. Extract team member entries from UAT
3. Report these as **"Missing from PROD (expected from UAT)"**

**For UAT plans** — If sections are empty/incomplete:
1. Fetch corresponding QA plan for the same version
2. Extract team member entries from QA
3. Report these as **"Missing from UAT (expected from QA)"**

**For QA plans** — No upstream comparison (QA is the source)

### Step 7: Generate Report

```markdown
## Deployment Plan Check: [Environment] [Version] [Date]

**Page**: [URL]
**Checked**: [timestamp]
**Team Filter**: [list of configured team members]

### MySQL Scripts
| Status | Team Member | Jira | File/Component |
|--------|-------------|------|----------------|
| ✅ | Name | PROJ-123 | filename.sql |
| ❌ Missing | Name | PROJ-456 | (expected from UAT/QA) |

### Bamboo Items
| Status | Team Member | Component | Jira |
|--------|-------------|-----------|------|
| ✅ Complete | Name | service-name | PROJ-123 |
| ⚠️ Incomplete | Name | service | PROJ-456 | Missing: Rollback Link |
| ❌ Missing | Name | service | (expected from UAT/QA) |

### Summary
- Team members in config: X
- Entries found: Y
- Complete: Z
- Incomplete: W
- Missing from upstream: V
- **Status: ✅ READY** or **❌ NOT READY**
```

---

## Example Usage

### Check a specific version's PROD readiness
```
User: Check the deployment plan for EVV 8.52

Claude:
1. Searches for "EVV 8.52 PROD"
2. Fetches PROD page
3. Finds MySQL Scripts and Bamboo Items are EMPTY for configured team
4. Fetches UAT plan for comparison
5. Reports: "PROD is NOT READY - missing X entries from UAT"
```

### Check a specific UAT environment
```
User: Check UAT20260106

Claude:
1. Searches for "UAT20260106"
2. Fetches page
3. Filters for configured team members only
4. If sections are empty, fetches QA plan for comparison
5. Reports complete/incomplete/missing entries for team
```

### Check a specific QA environment
```
User: Check QA20260107

Claude:
1. Searches for "QA20260107"
2. Fetches page
3. Filters for configured team members only
4. Reports complete/incomplete entries (QA is source, no upstream comparison)
```

### Check with URL
```
User: Check https://hhaxsupport.atlassian.net/wiki/spaces/FD/pages/123456789

Claude:
1. Extracts pageId 123456789
2. Fetches and parses
3. Reports team entries only
```

---

## Edge Cases

| Case | Handling |
|------|----------|
| Empty PROD plan | Fetch UAT, report missing entries |
| Empty UAT plan | Fetch QA, report missing entries |
| Empty QA plan | Report "No entries for configured team members" (QA is source) |
| No team entries in plan | Report "No entries for configured team members" |
| Team member in multiple entries | Report all entries for that member |
| Non-team members in plan | **Ignore completely** — do not report |
| PROD has entries but UAT has more | Report delta as missing |
| UAT has entries but QA has more | Report delta as missing |
