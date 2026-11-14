# Security notes

## Hard rules baked into this stack

1. **SSH stays enabled.** Firewall scripts always allow OpenSSH first.
2. **Chrome DevTools (CDP) binds to `127.0.0.1` only.** `launch-chrome.sh` refuses other hosts. UFW denies port 9222 from the network.
3. **RDP is not opened to the world by default.** Prefer `ssh -L 3389:127.0.0.1:3389`. Optional allowlist: `--allow-rdp-from YOUR_IP`.
4. **No CAPTCHA / MFA / checkpoint bypass.** Scripts stop and ask you to finish challenges over RDP.
5. **No silent publishing.** `reels prepare` never clicks Share. `reels confirm` requires `--i-understand`.
6. **No OpenAI API key in the default path.** Codex should use ChatGPT Go login.

## What you should still do

- Use SSH keys; disable password SSH if you are comfortable managing keys.
- Keep the VPS updated: `sudo apt update && sudo apt upgrade`.
- Restrict who can log into the Linux account that owns the Instagram Chrome profile.
- Treat `~/.aicomputer/chrome-profile` like a password vault (session cookies).
- Do not install random “Instagram growth” browser extensions.

## Instagram account risk

Automating the web UI can trigger Instagram security reviews. Use slow, intentional actions; complete checks yourself; avoid aggressive schedules. This project does not claim compliance with Instagram’s terms — you own that risk.
