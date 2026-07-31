---
name: codex
description: "Delegate coding to OpenAI Codex CLI (features, PRs)."
---

# Codex CLI

Delegate coding tasks to [Codex](https://github.com/openai/codex) through an
available shell-command tool. Codex is OpenAI's autonomous coding agent CLI.

## When to use

- Building features
- Refactoring
- PR reviews
- Batch issue fixing

Requires the codex CLI and a git repository.

## Prerequisites

- Codex installed: `npm install -g @openai/codex`
- OpenAI auth configured: either `OPENAI_API_KEY` or Codex OAuth credentials
  from the Codex CLI login flow
- **Must run inside a git repository** — Codex refuses to run outside one
- A PTY-capable terminal is required only for the interactive Codex TUI;
  non-interactive `codex exec` normally runs without one

The standalone Codex CLI may use either `OPENAI_API_KEY` or an existing CLI
OAuth session. Do not treat a missing `OPENAI_API_KEY` alone as proof that
Codex authentication is missing; verify with the CLI's own login/status flow.

## One-Shot Tasks

```
cd ~/project && codex exec 'Add dark mode toggle to settings'
```

For scratch work (Codex needs a git repo):
```
cd $(mktemp -d) && git init && codex exec 'Build a snake game in Python'
```

## Background Mode (Long Tasks)

```
# Start in background with PTY
cd ~/project && codex exec --sandbox workspace-write 'Refactor the auth module'
# Returns session_id

# Monitor progress
# Use the agent host's background-process controls to poll session <id>.
# Use the agent host's background-process controls to log session <id>.

# Send input if Codex asks a question
# Use the agent host's background-process controls to submit session <id>.

# Kill if needed
# Use the agent host's background-process controls to kill session <id>.
```

## Key Flags

| Flag | Effect |
|------|--------|
| `exec "prompt"` | One-shot execution, exits when done |
| `--sandbox workspace-write` (`-s`) | Sandboxed but auto-approves file changes in the workspace (the recommended auto-build mode) |
| `--dangerously-bypass-approvals-and-sandbox` | No sandbox, no approvals (fastest, most dangerous; `--yolo` still works as a hidden alias) |
| `--sandbox danger-full-access` | No Codex sandbox; useful when the host service context breaks bubblewrap |

> **Deprecated:** `--full-auto` still works but the live CLI warns to use `--sandbox workspace-write` instead.

## Constrained Service-Host Caveat

When invoking the Codex CLI from an already-containerized gateway or service host,
Codex `workspace-write` sandboxing may fail even
when the same command works in the user's interactive shell. A typical symptom is
bubblewrap/user-namespace errors such as `setting up uid map: Permission denied`
or `loopback: Failed RTM_NEWADDR: Operation not permitted`.

In that context, prefer:

```
codex exec --sandbox danger-full-access "<task>"
```

Use process boundaries as the safety layer instead: explicit `workdir`, clean git
status before launch, narrow task prompts, `git diff` review, targeted tests, and
human/agent confirmation before committing broad changes.

## PR Reviews

Clone to a temp directory for safe review:

```
REVIEW=$(mktemp -d) && git clone https://github.com/user/repo.git $REVIEW && cd $REVIEW && gh pr checkout 42 && codex review --base origin/main
```

## Parallel Issue Fixing with Worktrees

```
# Create worktrees
cd ~/project && git worktree add -b fix/issue-78 /tmp/issue-78 main
cd ~/project && git worktree add -b fix/issue-99 /tmp/issue-99 main

# Launch Codex in each
cd /tmp/issue-78 && codex --sandbox workspace-write exec 'Fix issue #78: <description>. Commit when done.'
cd /tmp/issue-99 && codex --sandbox workspace-write exec 'Fix issue #99: <description>. Commit when done.'

# Monitor
# Use the agent host's background-process controls to list.

# After completion, push and create PRs
cd /tmp/issue-78 && git push -u origin fix/issue-78
gh pr create --repo user/repo --head fix/issue-78 --title 'fix: ...' --body '...'

# Cleanup
cd ~/project && git worktree remove /tmp/issue-78
```

## Batch PR Reviews

```
# Fetch all PR refs
cd ~/project && git fetch origin '+refs/pull/*/head:refs/remotes/origin/pr/*'

# Review multiple PRs in parallel
cd ~/project && codex exec 'Review PR #86. git diff origin/main...origin/pr/86'
cd ~/project && codex exec 'Review PR #87. git diff origin/main...origin/pr/87'

# Post results
cd ~/project && gh pr comment 86 --body '<review>'
```

## Rules

1. **Use a PTY only for the interactive TUI** — `codex exec` is non-interactive and should use an ordinary subprocess unless the host or command specifically requires a PTY
2. **Git repo required** — Codex won't run outside a git directory. Use `mktemp -d && git init` for scratch
3. **Use `exec` for one-shots** — `codex exec "prompt"` runs and exits cleanly
4. **`--sandbox workspace-write` for building** — auto-approves changes within the sandbox (`--full-auto` is deprecated for this)
5. **Background for long tasks** — use `background=true` and monitor with `process` tool
6. **Don't interfere** — monitor with `poll`/`log`, be patient with long-running tasks
7. **Parallel is fine** — run multiple Codex processes at once for batch work
