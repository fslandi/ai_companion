# AI Computer — Ubuntu VPS + Chrome + Codex (Instagram Reels)

Remote desktop computer for an AI agent:

**Codex CLI (ChatGPT Go) → Ubuntu 24.04 → XFCE → Chrome (persistent login) → Instagram Reels**

This repository folder contains provisioning scripts and a small `aicomputer` CLI. You install and run it **on your VPS**.

## Quick links

- [Architecture](docs/architecture.md)
- [Setup](docs/setup.md)
- [Security](docs/security.md)
- [Reels usage](docs/usage-reels.md)
- [AGENTS.md](AGENTS.md) (instructions for Codex)

## Why this design

| Need | Choice |
|------|--------|
| See and use a real desktop | XFCE + xrdp (SSH tunnel) |
| Keep Instagram login | Chrome `--user-data-dir` under `~/.aicomputer/chrome-profile` |
| AI can click in the browser | Playwright attaches to Chrome CDP on `127.0.0.1` only |
| Use ChatGPT Go, not API billing | Codex CLI → Sign in with ChatGPT |
| No accidental posts | `reels prepare` then explicit `reels confirm --i-understand` |

## Bootstrap on the VPS

```bash
git clone https://github.com/fslandi/ai_companion.git ~/ai_companion
cd ~/ai_companion/ai_computer
bash scripts/00-check-resources.sh
sudo bash scripts/bootstrap.sh
```

Then follow [docs/setup.md](docs/setup.md).

## CLI cheat sheet

```bash
aicomputer doctor
aicomputer chrome start
aicomputer inbox
aicomputer reels prepare --video media/inbox/clip.mp4 --caption "Hello"
# review screenshot / RDP
aicomputer reels confirm --i-understand
aicomputer reels abort
```

## Cost stance

- VPS you already rent: yes
- ChatGPT Go → Codex CLI login: yes (plan limits; no separate API key by default)
- Extra paid cloud computer / browser SaaS: not required
- OpenAI Platform API key: **not configured** unless you later approve it
