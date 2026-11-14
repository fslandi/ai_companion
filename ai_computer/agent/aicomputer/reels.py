from __future__ import annotations

import shutil
import time
from datetime import datetime, timezone
from pathlib import Path

from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError, sync_playwright

from . import chrome as chrome_mod
from . import confirm as confirm_mod
from .config import Settings, load_settings

INSTAGRAM_HOME = "https://www.instagram.com/"
INSTAGRAM_CREATE_HINT = "https://www.instagram.com/"


class HumanActionRequired(RuntimeError):
    """Raised when Instagram needs a manual step (login, MFA, challenge)."""


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _screenshot(page: Page, settings: Settings, label: str) -> Path:
    settings.ensure_dirs()
    path = settings.screenshots_dir / f"{label}-{_timestamp()}.png"
    page.screenshot(path=str(path), full_page=False)
    return path


def _looks_logged_out(page: Page) -> bool:
    url = page.url.lower()
    if "accounts/login" in url or "/login" in url:
        return True
    # Login form markers
    for sel in ('input[name="username"]', 'input[name="email"]', 'text=Log in'):
        try:
            if page.locator(sel).first.is_visible(timeout=500):
                return True
        except PlaywrightTimeoutError:
            continue
        except Exception:
            continue
    return False


def _click_first(page: Page, selectors: list[str], timeout_ms: int = 4000) -> bool:
    for sel in selectors:
        loc = page.locator(sel).first
        try:
            loc.wait_for(state="visible", timeout=timeout_ms)
            loc.click(timeout=timeout_ms)
            return True
        except Exception:
            continue
    return False


def _fill_first(page: Page, selectors: list[str], text: str, timeout_ms: int = 4000) -> bool:
    for sel in selectors:
        loc = page.locator(sel).first
        try:
            loc.wait_for(state="visible", timeout=timeout_ms)
            loc.fill(text, timeout=timeout_ms)
            return True
        except Exception:
            continue
    return False


def _set_input_files(page: Page, video: Path) -> bool:
    # Instagram create dialog uses a hidden file input.
    candidates = [
        'input[type="file"][accept*="video"]',
        'input[type="file"][accept*="image"]',
        'input[type="file"]',
    ]
    for sel in candidates:
        loc = page.locator(sel)
        try:
            count = loc.count()
        except Exception:
            continue
        for i in range(count):
            try:
                loc.nth(i).set_input_files(str(video))
                return True
            except Exception:
                continue
    return False


def prepare_reel(
    video: Path,
    caption: str,
    *,
    settings: Settings | None = None,
    dry_run: bool = False,
) -> dict:
    """Open Instagram, stage a Reel, stop before Share, await human confirm."""
    settings = settings or load_settings()
    video = video.expanduser().resolve()
    if not video.is_file():
        raise FileNotFoundError(f"Video not found: {video}")

    # Keep a copy metadata trail under media/prepared
    settings.ensure_dirs()
    prepared_copy = settings.prepared_dir / f"{_timestamp()}_{video.name}"
    if video.resolve() != prepared_copy.resolve():
        shutil.copy2(video, prepared_copy)

    if dry_run:
        job = {
            "status": "awaiting_confirmation",
            "mode": "dry_run",
            "video": str(video),
            "prepared_copy": str(prepared_copy),
            "caption": caption,
            "screenshot": None,
            "note": "dry-run only; no browser actions",
        }
        confirm_mod.write_job(job, settings)
        return job

    with sync_playwright() as p:
        browser = chrome_mod.connect(p, settings)
        page = chrome_mod.first_page(browser)
        page.goto(INSTAGRAM_HOME, wait_until="domcontentloaded")
        time.sleep(2)

        if _looks_logged_out(page):
            shot = _screenshot(page, settings, "login-required")
            raise HumanActionRequired(
                "Instagram login required. Open RDP, sign in once in this Chrome "
                f"profile, complete any MFA manually, then retry. Screenshot: {shot}"
            )

        # Create (+) button — selectors change often; try several.
        opened = _click_first(
            page,
            [
                'svg[aria-label="New post"]',
                'svg[aria-label="Новая публикация"]',
                'a[href="#"][role="link"]:has(svg[aria-label="New post"])',
                'span:text-is("Create")',
                'span:text-is("Создать")',
                '[aria-label="New post"]',
                '[aria-label="Новая публикация"]',
            ],
            timeout_ms=5000,
        )
        if not opened:
            shot = _screenshot(page, settings, "create-not-found")
            raise HumanActionRequired(
                "Could not find Instagram Create button. UI may have changed or a "
                f"challenge dialog is open. Finish manually in RDP. Screenshot: {shot}"
            )

        time.sleep(1)
        # Prefer Reel if a chooser appears.
        _click_first(
            page,
            [
                'span:text-is("Reel")',
                'span:text-is("Reels")',
                'span:text-is("Клип")',
                'div[role="dialog"] >> text=Reel',
                'text=Reel',
            ],
            timeout_ms=3000,
        )

        time.sleep(1)
        if not _set_input_files(page, video):
            shot = _screenshot(page, settings, "file-input-missing")
            raise HumanActionRequired(
                "Could not attach the video via file input. Use RDP to select the "
                f"file manually, then continue with confirm only if Share is ready. "
                f"Screenshot: {shot}"
            )

        # Advance through crop / edit steps when Next is shown.
        for _ in range(4):
            advanced = _click_first(
                page,
                [
                    'div[role="button"]:text-is("Next")',
                    'button:text-is("Next")',
                    'div[role="button"]:text-is("Далее")',
                    'button:text-is("Далее")',
                    'text=Next',
                    'text=Далее',
                ],
                timeout_ms=2500,
            )
            if not advanced:
                break
            time.sleep(1.2)

        # Caption on the final compose screen.
        caption_filled = _fill_first(
            page,
            [
                'div[aria-label="Write a caption..."]',
                'div[aria-label="Напишите подпись..."]',
                'textarea[aria-label="Write a caption..."]',
                'div[role="textbox"]',
                'textarea',
            ],
            caption,
            timeout_ms=4000,
        )

        # CRITICAL: do not click Share / Publish here.
        shot = _screenshot(page, settings, "reels-awaiting-confirm")
        job = {
            "status": "awaiting_confirmation",
            "video": str(video),
            "prepared_copy": str(prepared_copy),
            "caption": caption,
            "caption_filled": caption_filled,
            "screenshot": str(shot),
            "page_url": page.url,
            "note": (
                "Prepared only. Review the screenshot or RDP desktop, then run "
                "`aicomputer reels confirm` to publish, or `aicomputer reels abort`."
            ),
        }
        confirm_mod.write_job(job, settings)
        return job


def confirm_publish(*, settings: Settings | None = None) -> dict:
    """Click Share/Publish for the prepared job after human approval."""
    settings = settings or load_settings()
    job = confirm_mod.require_prepared(settings)

    with sync_playwright() as p:
        browser = chrome_mod.connect(p, settings)
        page = chrome_mod.first_page(browser)

        shared = _click_first(
            page,
            [
                'div[role="button"]:text-is("Share")',
                'button:text-is("Share")',
                'div[role="button"]:text-is("Поделиться")',
                'button:text-is("Поделиться")',
                'text=Share',
                'text=Поделиться',
            ],
            timeout_ms=5000,
        )
        if not shared:
            shot = _screenshot(page, settings, "share-not-found")
            raise HumanActionRequired(
                "Share button not found. The create dialog may have closed or Instagram "
                f"changed the UI. Publish manually in RDP if the draft is still open. "
                f"Screenshot: {shot}"
            )

        time.sleep(2)
        shot = _screenshot(page, settings, "reels-shared")
        done = {
            **job,
            "status": "published_clicked",
            "confirm_screenshot": str(shot),
            "note": (
                "Share was clicked. Instagram may still be uploading; verify in the app "
                "or on the desktop. No CAPTCHA/MFA bypass was attempted."
            ),
        }
        confirm_mod.write_job(done, settings)
        return done


def abort(*, settings: Settings | None = None) -> dict:
    settings = settings or load_settings()
    job = confirm_mod.read_job(settings) or {}
    confirm_mod.clear_job(settings)
    return {"status": "aborted", "previous": job}
