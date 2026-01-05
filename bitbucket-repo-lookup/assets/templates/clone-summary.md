# Clone Summary Template

Use this template format when displaying clone operation results.

---

## Single Repository Clone

```
Cloning {repo_name}...

✓ Successfully cloned {repo_name}
  Location:    {clone_path}
  Branch:      {main_branch}
  Size:        {size_mb} MB
  Last commit: "{commit_message}" ({time_ago})
  Author:      {commit_author}
```

---

## Multiple Repository Clone (Progress)

Show progress during bulk clone operations:

```
Cloning 5 repositories to {base_directory}...

[1/5] Cloning user-service...
      ✓ Cloned to {path}/user-service

[2/5] Cloning payment-gateway...
      ✓ Cloned to {path}/payment-gateway

[3/5] Cloning web-dashboard...
      ✓ Cloned to {path}/web-dashboard

[4/5] Cloning notification-service...
      ✗ Failed: Permission denied

[5/5] Cloning shared-utils...
      ✓ Cloned to {path}/shared-utils
```

---

## Bulk Clone Summary

After completing bulk clone:

```
═══════════════════════════════════════════════════════════════════════════
                           CLONE SUMMARY
═══════════════════════════════════════════════════════════════════════════

Workspace:   {workspace}
Destination: {base_directory}
Method:      {clone_method} (HTTPS/SSH)

───────────────────────────────────────────────────────────────────────────
SUCCESSFUL ({success_count}/{total_count})
───────────────────────────────────────────────────────────────────────────

│ Repository            │ Path                              │ Size     │
├───────────────────────┼───────────────────────────────────┼──────────┤
│ user-service          │ ~/repos/backend/user-service      │ 45.2 MB  │
│ payment-gateway       │ ~/repos/backend/payment-gateway   │ 32.1 MB  │
│ web-dashboard         │ ~/repos/frontend/web-dashboard    │ 128.7 MB │
│ shared-utils          │ ~/repos/libraries/shared-utils    │ 8.4 MB   │

Total size: {total_size_mb} MB

───────────────────────────────────────────────────────────────────────────
FAILED ({failed_count}/{total_count})
───────────────────────────────────────────────────────────────────────────

│ Repository            │ Error                                         │
├───────────────────────┼───────────────────────────────────────────────┤
│ notification-service  │ Permission denied - check repository access   │

───────────────────────────────────────────────────────────────────────────
SKIPPED ({skipped_count}/{total_count})
───────────────────────────────────────────────────────────────────────────

│ Repository            │ Reason                                        │
├───────────────────────┼───────────────────────────────────────────────┤
│ old-service           │ Already exists at ~/repos/backend/old-service │

═══════════════════════════════════════════════════════════════════════════
```

---

## Success Summary (All Successful)

```
✓ Successfully cloned {count} repositories

Total size: {total_size_mb} MB
Location:   {base_directory}

Repositories:
  • user-service          → ~/repos/backend/user-service
  • payment-gateway       → ~/repos/backend/payment-gateway
  • web-dashboard         → ~/repos/frontend/web-dashboard
  • shared-utils          → ~/repos/libraries/shared-utils

All repositories are ready for development!
```

---

## Partial Success Summary

```
⚠ Cloned {success_count} of {total_count} repositories

Successful:
  ✓ user-service
  ✓ payment-gateway
  ✓ web-dashboard

Failed:
  ✗ notification-service - Permission denied

Would you like to:
• "Retry failed" - Attempt to clone failed repositories again
• "Skip failed" - Continue with successful clones only
• "Check permissions" - View your access level for failed repos
```

---

## All Failed Summary

```
✗ Failed to clone any repositories

Attempted: {total_count} repositories
Errors:
  • notification-service - Permission denied
  • secret-service - Repository not found
  • internal-tools - Authentication failed

Common causes:
1. Invalid or expired app password
2. Missing repository read permissions
3. Incorrect workspace slug
4. Network connectivity issues

Troubleshooting:
• Verify credentials in config.md
• Check Bitbucket app password permissions
• Ensure network connectivity
• Try cloning a single repository first
```

---

## Already Exists Handling

When repository directory already exists:

```
Repository 'user-service' already exists at ~/repos/backend/user-service

Options:
• "Skip" - Leave existing repository unchanged
• "Update" - Pull latest changes (git pull)
• "Replace" - Delete and re-clone (WARNING: loses local changes)
• "Rename" - Clone to user-service-{timestamp}
```

---

## Clone Confirmation (Bulk)

Before cloning many repositories:

```
You're about to clone {count} repositories:

│ # │ Repository            │ Size (est.) │
├───┼───────────────────────┼─────────────┤
│ 1 │ user-service          │ ~45 MB      │
│ 2 │ payment-gateway       │ ~32 MB      │
│ 3 │ web-dashboard         │ ~128 MB     │
│ 4 │ notification-service  │ ~18 MB      │
│ 5 │ shared-utils          │ ~8 MB       │

Estimated total size: ~231 MB
Destination: {base_directory}

Proceed with clone? (yes/no/select different repos)
```

---

## Error Messages

### Authentication Error
```
✗ Authentication failed

Unable to authenticate with Bitbucket. Please check:
• Username is correct in config.md
• App password is valid and not expired
• App password has 'Repositories: Read' permission

To create a new app password:
1. Go to Bitbucket → Personal settings → App passwords
2. Create new password with repository read access
3. Update config.md with new credentials
```

### Network Error
```
✗ Network error during clone

Failed to connect to Bitbucket. Please check:
• Internet connectivity
• Firewall/proxy settings
• Bitbucket service status: https://bitbucket.status.atlassian.com/

Retrying in {retry_delay} seconds... (attempt {attempt}/{max_attempts})
```

### Permission Error
```
✗ Permission denied for {repo_name}

You don't have access to clone this repository.

To request access:
1. Contact the repository administrator
2. Request 'Read' permission for the repository
3. Or ask to be added to a group with access

Repository URL: {html_url}
```

---

## Post-Clone Actions

After successful clone, suggest next steps:

```
Next steps:
• cd {clone_path}              - Navigate to repository
• git status                   - Check repository status
• git log --oneline -5         - View recent commits
• code .                       - Open in VS Code
```
