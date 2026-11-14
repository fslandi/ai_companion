# Setup (Ubuntu 24.04 VPS)

You run these steps **on your VPS**. This Cloud Agent cannot reach your server.

## 0. Clone and check resources

```bash
sudo apt-get update
sudo apt-get install -y git
git clone https://github.com/fslandi/ai_companion.git ~/ai_companion
cd ~/ai_companion/ai_computer
bash scripts/00-check-resources.sh
```

If RAM is under ~2 GiB, add swap before the desktop:

```bash
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

## 1. Bootstrap (recommended)

```bash
cd ~/ai_companion/ai_computer
sudo bash scripts/bootstrap.sh
# optional: allow RDP only from your home IP instead of tunnel-only
# sudo bash scripts/bootstrap.sh --allow-rdp-from YOUR.PUBLIC.IP
```

Or run scripts `01`…`06` individually.

## 2. Remote desktop (safe default)

Do **not** open port 3389 to the whole internet unless you must.

From your laptop:

```bash
ssh -N -L 3389:127.0.0.1:3389 YOUR_USER@YOUR_VPS_IP
```

Then connect an RDP client to `127.0.0.1:3389` with your Linux username/password.

Inside the desktop, confirm:

```bash
echo $DISPLAY
```

If needed, put that value into `~/.config/aicomputer/chrome.env` (see `chrome/chrome.env.example`).

## 3. Chrome + Instagram session

In the RDP session:

```bash
export PATH="$HOME/.local/bin:$PATH"
aicomputer chrome start
```

A Chrome window opens with a dedicated profile under `~/.aicomputer/chrome-profile`.

1. Log into Instagram once.
2. Complete any MFA / checkpoint yourself.
3. Close nothing special — profile cookies persist across restarts.

Verify CDP is local only:

```bash
aicomputer chrome status
# should show http://127.0.0.1:9222
ss -lntp | grep 9222   # must show 127.0.0.1, not 0.0.0.0
```

## 4. Codex CLI (ChatGPT Go — no API key)

```bash
codex login
```

Choose **Sign in with ChatGPT**. This uses your ChatGPT Go plan allowance.

Do **not** use `codex login --with-api-key` unless you explicitly accept OpenAI API billing.

Open this folder in Codex:

```bash
cd ~/ai_companion/ai_computer
codex
```

`AGENTS.md` in this directory explains the Reels workflow.

## 5. Transfer videos

```bash
scp ./my-reel.mp4 YOUR_USER@YOUR_VPS_IP:~/ai_companion/ai_computer/media/inbox/
```

Or use SFTP / Drag-and-drop in some RDP clients.

## 6. First Reels dry run

```bash
aicomputer doctor
aicomputer reels prepare --video ~/ai_companion/ai_computer/media/inbox/my-reel.mp4 \
  --caption "Test caption" --dry-run
aicomputer reels status
aicomputer reels abort
```

Then a real prepare (still no publish):

```bash
aicomputer chrome start
aicomputer reels prepare --video ~/ai_companion/ai_computer/media/inbox/my-reel.mp4 \
  --caption "Test caption"
# review ~/.aicomputer/screenshots or the RDP window
aicomputer reels confirm --i-understand
```

## Optional systemd user unit

```bash
mkdir -p ~/.config/systemd/user ~/.config/aicomputer
cp chrome/chrome.env.example ~/.config/aicomputer/chrome.env
# edit paths + DISPLAY
# Edit ExecStart in the unit to the absolute path of launch-chrome.sh on this machine
cp systemd/aicomputer-chrome.service ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now aicomputer-chrome.service
```
