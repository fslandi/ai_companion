# AGENTS.md — Codex / AI operator notes

You are working on a remote Ubuntu “AI Computer” used to control a real Chrome browser for Instagram Reels.

## Non-negotiables

- Prefer the `aicomputer` CLI over inventing one-off CDP scripts.
- Never publish a Reel without an explicit human approval step.
- Never click Share during `prepare`. Only `aicomputer reels confirm --i-understand` publishes.
- Never expose Chrome CDP beyond `127.0.0.1`.
- Never install or use CAPTCHA solvers, MFA bypasses, or unofficial Instagram private APIs.
- Never configure OpenAI API key billing unless the human explicitly asks for API billing.
- If Instagram shows login, MFA, checkpoint, or CAPTCHA: stop and tell the human to finish it in RDP.

## Standard Reels workflow

1. `aicomputer doctor`
2. `aicomputer chrome start` (needs an active graphical session / correct `DISPLAY`)
3. `aicomputer inbox` — pick a video under `media/inbox/`
4. `aicomputer reels prepare --video PATH --caption "..."`
5. Show the human the screenshot path from the JSON output and wait.
6. Only after clear approval: `aicomputer reels confirm --i-understand`
7. On cancel: `aicomputer reels abort`

## Useful paths

- Profile / cookies: `~/.aicomputer/chrome-profile`
- Job state: `~/.aicomputer/state/reels_job.json`
- Screenshots: `~/.aicomputer/screenshots/`
- Videos: `ai_computer/media/inbox/`

## Auth for yourself (Codex)

Sign in with ChatGPT (Go plan). Do not use `--with-api-key` by default.
