# Repository Listing Template

Use this template format when displaying repository listings to users.

---

## Compact List Format (Default)

```
┌──────────────────────────────────────────────────────────────────────────┐
│ # │ Repository Name      │ Project    │ Language   │ Updated            │
├──────────────────────────────────────────────────────────────────────────┤
│ 1 │ {repo_name}          │ {project}  │ {language} │ {updated_date}     │
│ 2 │ {repo_name}          │ {project}  │ {language} │ {updated_date}     │
│ 3 │ {repo_name}          │ {project}  │ {language} │ {updated_date}     │
└──────────────────────────────────────────────────────────────────────────┘

Found {count} repositories in workspace '{workspace}'.
```

---

## Selection Prompt

After listing, always include selection options:

```
Which repositories would you like to clone?
• By number: "Clone 1, 3, 5" or "Clone 1-5"
• By name: "Clone user-service and payment-gateway"
• All repos: "Clone all" or "Download everything"
• Filter more: "Show only Python repos" or "Filter by project backend"
• Cancel: "None" or "Cancel"
```

---

## Verbose List Format

When user requests detailed view or `output.verbose: true`:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ 1. {repo_name}                                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│ Project:     {project_name} ({project_key})                                 │
│ Description: {description}                                                  │
│ Language:    {language}                                                     │
│ Size:        {size_mb} MB                                                   │
│ Main Branch: {main_branch}                                                  │
│ Created:     {created_date}                                                 │
│ Updated:     {updated_date}                                                 │
│ Private:     {is_private}                                                   │
│ URL:         {html_url}                                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│ Clone (HTTPS): git clone {https_clone_url}                                  │
│ Clone (SSH):   git clone {ssh_clone_url}                                    │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Grouped by Project Format

When repositories span multiple projects:

```
## Backend Services (BACKEND)

│ # │ Repository Name      │ Language   │ Updated     │
├───┼──────────────────────┼────────────┼─────────────┤
│ 1 │ user-service         │ Python     │ 2024-01-15  │
│ 2 │ payment-gateway      │ Go         │ 2024-01-14  │
│ 3 │ notification-service │ Python     │ 2024-01-10  │

## Frontend (FRONTEND)

│ # │ Repository Name      │ Language   │ Updated     │
├───┼──────────────────────┼────────────┼─────────────┤
│ 4 │ web-dashboard        │ TypeScript │ 2024-01-13  │
│ 5 │ admin-portal         │ TypeScript │ 2024-01-08  │

## Mobile (MOBILE)

│ # │ Repository Name      │ Language   │ Updated     │
├───┼──────────────────────┼────────────┼─────────────┤
│ 6 │ ios-app              │ Swift      │ 2024-01-12  │
│ 7 │ android-app          │ Kotlin     │ 2024-01-11  │

Found 7 repositories across 3 projects.
```

---

## Empty Results

When no repositories match the query:

```
No repositories found in workspace '{workspace}'.

Possible reasons:
• The workspace slug may be incorrect
• You may not have access to any repositories
• Your filter may be too restrictive

Try:
• Check workspace slug in config.md
• Remove filters: "List all repositories"
• Verify your Bitbucket permissions
```

---

## Filtered Results

When displaying filtered results:

```
Showing {count} of {total} repositories
Filter: {filter_description}

┌──────────────────────────────────────────────────────────────────────────┐
│ # │ Repository Name      │ Project    │ Language   │ Updated            │
...

To see all repositories: "List all repos" or "Remove filter"
```

---

## Field Formatting Rules

| Field       | Format                                     |
|-------------|--------------------------------------------|
| Name        | Truncate at 20 chars, add `...` if needed  |
| Project     | Use project key, truncate at 10 chars      |
| Language    | Capitalize, "N/A" if not detected          |
| Date        | YYYY-MM-DD format                          |
| Size        | Convert to MB with 1 decimal place         |
| Description | First 50 chars, add `...` if truncated     |
| Boolean     | "Yes" / "No"                               |

---

## Pagination Message

When results span multiple pages:

```
Showing repositories 1-50 of {total}.

• "Show more" or "Next page" for repositories 51-100
• "Show all" to display complete list (may be slow for large workspaces)
```
