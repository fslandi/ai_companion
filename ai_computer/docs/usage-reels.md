# Publishing Instagram Reels (human confirmation)

## Flow

```
drop video → chrome start → reels prepare → YOU review → reels confirm
```

1. Put a video in `media/inbox/` (mp4 recommended).
2. Ensure desktop Chrome is running with your logged-in Instagram profile:
   ```bash
   aicomputer chrome start
   ```
3. Prepare (stops before Share):
   ```bash
   aicomputer reels prepare \
     --video ~/ai_companion/ai_computer/media/inbox/clip.mp4 \
     --caption "Caption text #tags"
   ```
4. Review:
   - screenshot under `~/.aicomputer/screenshots/reels-awaiting-confirm-*.png`
   - or the live Create dialog in RDP
5. Publish only if it looks right:
   ```bash
   aicomputer reels confirm --i-understand
   ```
6. Or cancel:
   ```bash
   aicomputer reels abort
   ```

## Asking Codex

From `~/ai_companion/ai_computer`:

```text
Prepare an Instagram Reel from media/inbox/clip.mp4 with caption "...".
Do not publish. Stop for my confirmation.
```

After you approve in chat or after reviewing the screenshot:

```text
I reviewed the prepared Reel. Run confirm with --i-understand.
```

## When UI selectors break

Instagram changes their DOM often. If prepare fails with `HUMAN_ACTION_REQUIRED`:

1. Open RDP and finish the Create dialog manually up to the caption screen.
2. Either publish yourself, or leave Share visible and try `aicomputer reels confirm --i-understand`.
3. Open an issue / ask Cursor to update selectors in `agent/aicomputer/reels.py`.

## What this will not do

- Bypass CAPTCHA, MFA, or “suspicious login” checkpoints
- Drive Chrome DevTools over the public internet
- Call OpenAI APIs with a billed API key unless you choose that later
