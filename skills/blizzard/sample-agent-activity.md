# Sample Agent Activity Log

This is the format for blizzard teammate activity logs. Each agent maintains their own log file at the documentation root provided by the snowflake. Write entries as you work — don't batch them at the end.

## Format

```markdown
# <agent-name> — Activity Log

## YYYY-MM-DD HH:MM
<What you did, what you found, or what you decided. Keep it brief but specific enough that someone reading it later can understand what was happening at this point.>

## YYYY-MM-DD HH:MM
<Next entry>
```

## Example

```markdown
# developer — Activity Log

## 2026-03-30 14:02
Assigned to fix login timeout. Reading auth controller at alpha/src/api/auth.controller.ts.

## 2026-03-30 14:08
Found the issue — session TTL hardcoded to 30s instead of reading from config. Fixed in auth.config.ts and auth.controller.ts.

## 2026-03-30 14:12
Reported fix to snowflake. Waiting for verification.

## 2026-03-30 14:20
Backend-verifier found the fix works for normal login but the refresh token path still uses the old hardcoded value. Fixing auth.refresh.ts now.

## 2026-03-30 14:25
Fixed refresh path. Reported to snowflake for re-verification.
```

## Guidelines

- **Timestamp every entry** — Use `YYYY-MM-DD HH:MM` format
- **Write as you go** — Don't wait until you're done. If you're reading code, say so. If you hit a dead end, say so.
- **Be specific** — Include file paths, entity names, error messages. "Fixed the bug" is not useful. "Fixed TTL in auth.config.ts line 42" is.
- **Include setbacks** — Dead ends, wrong assumptions, and errors are valuable information for the retrospective
- **Keep it concise** — 1-3 sentences per entry. This is a log, not a narrative
