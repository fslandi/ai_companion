# Architecture: AI Computer for Instagram Reels

## Goal

Turn an Ubuntu 24.04 VPS into a remote computer that an AI agent (Codex CLI via ChatGPT Go) can use like a desk: graphical desktop, persistent Chrome session, file inbox, and controlled browser actions for preparing Instagram Reels.

## Chosen stack

```
You / Cursor
    └── SSH
         └── Ubuntu 24.04 VPS
              ├── XFCE desktop
              ├── xrdp (RDP; prefer SSH tunnel)
              ├── Google Chrome (persistent profile)
              │     └── CDP on 127.0.0.1:9222 only
              ├── Playwright agent (`aicomputer`)
              │     └── prepare → human confirm → publish
              └── Codex CLI (sign in with ChatGPT Go)
```

### Why these components

| Component | Choice | Why |
|-----------|--------|-----|
| Desktop | XFCE | Light, stable on small VPS RAM |
| Remote UI | xrdp + SSH tunnel | Simple on Windows/macOS; no public noVNC surface by default |
| Browser | Google Chrome | Best Instagram web compatibility; persistent `--user-data-dir` |
| Control | Playwright → CDP | Real browser UI control; attaches to the same visible Chrome session |
| AI | Codex CLI + ChatGPT Go login | Uses existing Go plan; **no OpenAI API key / usage billing** |
| Publish gate | Explicit confirm step | Agent prepares; you approve before Share |

### Rejected / deferred alternatives

- **noVNC in browser** — useful later, but extra moving parts (websockify, TLS, reverse proxy). xrdp + tunnel is enough for v1.
- **Headless-only Chromium** — cheaper, but you cannot “see and click” like a real computer; weaker for Instagram challenges.
- **Selenium** — works, but Playwright is simpler for modern SPAs.
- **Paid cloud computers / extra AI APIs** — unnecessary given your VPS + ChatGPT Go.
- **Instagram unofficial APIs / CAPTCHA solvers** — out of scope and against your rules.

## Data and session layout

Default home for the stack (override with `AICOMPUTER_HOME`):

```
~/.aicomputer/
  chrome-profile/     # cookies, Instagram login
  state/              # prepare/confirm job state
  screenshots/        # pre-publish proof
  logs/
```

Repo paths on the VPS (after clone):

```
ai_computer/
  media/inbox/        # drop video files here (scp/sftp)
  media/prepared/     # optional copies / metadata
```

## Security model (v1)

1. **SSH stays on.** Do not disable it.
2. **UFW** allows SSH; RDP (3389) is either localhost-only via tunnel or restricted to your IP.
3. **Chrome CDP** binds to `127.0.0.1` only — never `0.0.0.0`.
4. No CAPTCHA/MFA bypass. If Instagram challenges you, finish it yourself over RDP.
5. Agent never auto-publishes in the default flow: `reels prepare` then `reels confirm`.

## Agent responsibilities

Codex (or you) should call the CLI tools rather than inventing raw CDP scripts each time:

1. `aicomputer doctor` — resources and service health
2. `aicomputer chrome start` — desktop Chrome with profile + local CDP
3. `aicomputer reels prepare --video … --caption …` — stop before Share
4. You review screenshot / RDP desktop
5. `aicomputer reels confirm` — only after your OK

`AGENTS.md` in this folder tells Codex exactly that workflow.
