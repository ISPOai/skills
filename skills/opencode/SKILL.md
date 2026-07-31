---
name: opencode
description: "Delegate coding to OpenCode CLI (features, PR review)."
---

# OpenCode CLI

Use [OpenCode](https://opencode.ai) as an autonomous coding worker from a local
agent's shell. OpenCode is a provider-agnostic, open-source AI coding agent with
a TUI and CLI.

Use the current runtime's shell for commands and its PTY/session support for an
interactive TUI. No provider-specific tool names are required.

## When to Use

- User explicitly asks to use OpenCode
- You want an external coding agent to implement/refactor/review code
- You need long-running coding sessions with progress checks
- You want parallel task execution in isolated workdirs/worktrees

OpenCode can modify files, run commands, commit, and interact with remotes.
Constrain it to the user's requested repository and task. Review its diff and
test results before accepting changes, and never infer permission to commit,
push, open a PR, or mutate external systems from a request to analyze or review.

## Prerequisites

- OpenCode installed: `npm i -g opencode-ai@latest` or `brew install anomalyco/tap/opencode`
- Auth configured: `opencode auth login` or set provider env vars (OPENROUTER_API_KEY, etc.)
- Verify: `opencode auth list` should show at least one provider
- Git repository for code tasks (recommended)
- `pty=true` for interactive TUI sessions

## Binary Resolution (Important)

Shell environments may resolve different OpenCode binaries. If behavior differs
between the user's terminal and the agent shell, check:

```
which -a opencode
opencode --version
```

If needed, pin an explicit binary path:

```
cd ~/project
$HOME/.opencode/bin/opencode run '...'
```

## One-Shot Tasks

Use `opencode run` for bounded, non-interactive tasks:

```
cd ~/project
opencode run 'Add retry logic to API calls and update tests'
```

Attach context files with `-f`:

```
opencode run 'Review this config for security issues' -f config.yaml -f .env.example
```

Show model thinking with `--thinking`:

```
opencode run 'Debug why tests fail in CI' --thinking
```

Force a specific model:

```
opencode run 'Refactor auth module' --model openrouter/anthropic/claude-sonnet-4
```

## Interactive Sessions (Background)

For iterative work requiring multiple exchanges, start `opencode` in `~/project`
with the runtime's PTY-capable background-session support. Send prompts through
that session, poll its output, and send Ctrl+C to exit. Do not use `/exit`; it
opens an agent selector instead of exiting.

### TUI Keybindings

| Key | Action |
|-----|--------|
| `Enter` | Submit message (press twice if needed) |
| `Tab` | Switch between agents (build/plan) |
| `Ctrl+P` | Open command palette |
| `Ctrl+X L` | Switch session |
| `Ctrl+X M` | Switch model |
| `Ctrl+X N` | New session |
| `Ctrl+X E` | Open editor |
| `Ctrl+C` | Exit OpenCode |

### Resuming Sessions

After exiting, OpenCode prints a session ID. Resume with:

```
cd ~/project
opencode -c                 # Continue last session
opencode -s ses_abc123      # Continue a specific session
```

## Common Flags

| Flag | Use |
|------|-----|
| `run 'prompt'` | One-shot execution and exit |
| `--continue` / `-c` | Continue the last OpenCode session |
| `--session <id>` / `-s` | Continue a specific session |
| `--agent <name>` | Choose OpenCode agent (build or plan) |
| `--model provider/model` | Force specific model |
| `--format json` | Machine-readable output/events |
| `--file <path>` / `-f` | Attach file(s) to the message |
| `--thinking` | Show model thinking blocks |
| `--variant <level>` | Reasoning effort (high, max, minimal) |
| `--title <name>` | Name the session |
| `--attach <url>` | Connect to a running opencode server |

## Procedure

1. Verify tool readiness:
   - `opencode --version`
   - `opencode auth list`
2. For bounded tasks, use `opencode run '...'` (no pty needed).
3. For iterative tasks, start `opencode` in a PTY-capable background session.
4. Monitor long tasks through that session's output.
5. If OpenCode asks for input, respond through the same session.
6. Exit by sending Ctrl+C or terminating only the resolved OpenCode process.
7. Summarize file changes, test results, and next steps back to user.

## PR Review Workflow

OpenCode has a built-in PR command:

```
cd ~/project
opencode pr 42
```

Or review in a temporary clone for isolation:

```
REVIEW=$(mktemp -d)
git clone https://github.com/user/repo.git "$REVIEW"
cd "$REVIEW"
opencode run 'Review this PR vs main. Report bugs, security risks, test gaps, and style issues.'
```

## Parallel Work Pattern

Use separate workdirs/worktrees to avoid collisions:

```
cd /tmp/issue-101 && opencode run 'Fix issue #101 and commit'
cd /tmp/issue-102 && opencode run 'Add parser regression tests and commit'
```

## Session & Cost Management

List past sessions:

```
opencode session list
```

Check token usage and costs:

```
opencode stats
opencode stats --days 7 --models anthropic/claude-sonnet-4
```

## Pitfalls

- Interactive `opencode` (TUI) sessions require `pty=true`. The `opencode run` command does NOT need pty.
- `/exit` is NOT a valid command — it opens an agent selector. Use Ctrl+C to exit the TUI.
- PATH mismatch can select the wrong OpenCode binary/model config.
- If OpenCode appears stuck, inspect the background session's logs before
  terminating it.
- Avoid sharing one working directory across parallel OpenCode sessions.
- Enter may need to be pressed twice to submit in the TUI (once to finalize text, once to send).

## Verification

Smoke test:

```
opencode run 'Respond with exactly: OPENCODE_SMOKE_OK'
```

Success criteria:
- Output includes `OPENCODE_SMOKE_OK`
- Command exits without provider/model errors
- For code tasks: expected files changed and tests pass

## Rules

1. Prefer `opencode run` for one-shot automation — it's simpler and doesn't need pty.
2. Use interactive background mode only when iteration is needed.
3. Always scope OpenCode sessions to a single repo/workdir.
4. For long tasks, provide progress updates from the background session's logs.
5. Report concrete outcomes (files changed, tests, remaining risks).
6. Exit interactive sessions with Ctrl+C or kill, never `/exit`.
