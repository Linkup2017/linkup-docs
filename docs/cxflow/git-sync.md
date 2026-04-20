# Git Sync

The **CxFlow Git Sync** (`lu_cxflow_git_sync`) module enables bidirectional
synchronization between CxFlow documents and Git repositories.

## Overview

```{mermaid}
graph LR
    ODOO[CxFlow Documents] -- Auto-push on save --> GIT[Git Repository]
    GIT -- Cron auto-pull --> ODOO
```

Documents are stored as Markdown files in the Git repository, preserving the
SSOT principle — what you see in CxFlow is what you get in Git.

## Setting Up a Git Repository

Navigate to **CxFlow → Git Sync → Repositories** and create a new record.

### Configuration Fields

| Field | Description | Required |
|---|---|---|
| **Repository URL** | HTTPS or SSH URL | Yes |
| **Branch** | Target branch (default: `main`) | Yes |
| **Auth Method** | `none`, `pat` (Personal Access Token), `ssh` | Yes |
| **Access Token** | Token for HTTPS auth | If PAT |
| **SSH Key Path** | Server path to SSH key | If SSH |
| **Auto Push** | Push to Git on every document save | No |
| **Auto Pull (Cron)** | Periodically pull from Git | No |
| **Sync Scope** | `all`, `cps`, `deliverable`, `report`, `note` | Yes |

```{warning}
Auto Push and Auto Pull are mutually exclusive — enable one or the other to
avoid sync conflicts.
```

### Constraint

Only one Git repository can be configured per project.

## Sync Operations

### Test Connection

Click **Test Connection** to validate credentials and confirm the repository
is accessible. This clones the repo to a temporary directory.

### Full Export

**Full Export** pushes all project documents (filtered by sync scope) to the
Git repository in a single operation. Use this for initial setup.

### Full Import

**Full Import** pulls all documents from Git and overwrites local content.

```{warning}
Full Import overwrites local `md_source`. Use with caution — consider
exporting first as a backup.
```

### Auto Push

When `auto_push` is enabled, every document save triggers an automatic Git
push for that document. The mixin extension tracks:

| Field | Description |
|---|---|
| `git_sync_path` | File path in the repository |
| `git_sync_sha` | SHA-256 hash (first 16 chars) of `md_source` |
| `git_last_synced_at` | Timestamp of last sync |
| `git_last_synced_version` | Document version at last sync |

### Auto Pull (Cron)

When `auto_pull_cron` is enabled, the hourly cron job automatically pulls
changes from the repository.

## State Machine

```{mermaid}
stateDiagram-v2
    [*] --> draft
    draft --> ready: Test Connection OK
    ready --> syncing: Sync starts
    syncing --> ready: Sync success
    syncing --> error: Sync failure
    error --> ready: Manual recovery
```

The cron job also recovers stuck repositories — if a repo has been in `syncing`
state for more than 10 minutes, it is automatically reset.

## Sync Log

Every sync operation creates a log entry in `lu.cxflow.git.sync.log`:

| Field | Description |
|---|---|
| `direction` | `export` or `import` |
| `state` | `success`, `conflict`, `error` |
| `doc_model` / `doc_id` | Affected document |
| `file_path` | Path in Git repository |
| `commit_sha` | Git commit hash |
| `db_version` | Document version at sync time |

Use the log to diagnose sync issues and track document change history across
both systems.

## Cron Job

| Cron | Schedule | Default State |
|---|---|---|
| CxFlow Git Auto Sync | Every 1 hour | **Inactive** (enable manually) |

The cron performs two tasks:

1. Recovers stuck repos (syncing > 10 min)
2. Pulls from repos with `auto_pull_cron=True` that are in `ready` or `error` state

## Dependencies

- **Python**: `PyYAML`
- **System**: `git` binary must be available on the server
