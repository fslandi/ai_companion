from __future__ import annotations

import json
import subprocess
import urllib.error
import urllib.request
from pathlib import Path

from playwright.sync_api import Browser, Page, Playwright, sync_playwright

from .config import Settings, load_settings


def repo_launch_script() -> Path:
    return Path(__file__).resolve().parents[2] / "chrome" / "launch-chrome.sh"


def cdp_version(settings: Settings | None = None) -> dict | None:
    settings = settings or load_settings()
    url = f"{settings.cdp_url}/json/version"
    try:
        with urllib.request.urlopen(url, timeout=2) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        return None


def start_chrome(settings: Settings | None = None) -> dict:
    settings = settings or load_settings()
    existing = cdp_version(settings)
    if existing:
        return existing
    script = repo_launch_script()
    if not script.exists():
        raise FileNotFoundError(f"Missing launch script: {script}")
    env = {
        **dict(**{k: v for k, v in __import__("os").environ.items()}),
        "AICOMPUTER_HOME": str(settings.home),
        "CHROME_PROFILE_DIR": str(settings.profile_dir),
        "CHROME_CDP_HOST": settings.cdp_host,
        "CHROME_CDP_PORT": str(settings.cdp_port),
    }
    subprocess.run(["bash", str(script)], check=True, env=env)
    info = cdp_version(settings)
    if not info:
        raise RuntimeError("Chrome started but CDP is not reachable on localhost.")
    return info


def connect(playwright: Playwright, settings: Settings | None = None) -> Browser:
    settings = settings or load_settings()
    if not cdp_version(settings):
        raise RuntimeError(
            "Chrome CDP not reachable. Start desktop Chrome with: aicomputer chrome start"
        )
    return playwright.chromium.connect_over_cdp(settings.cdp_url)


def first_page(browser: Browser) -> Page:
    if browser.contexts:
        ctx = browser.contexts[0]
        if ctx.pages:
            return ctx.pages[0]
        return ctx.new_page()
    ctx = browser.new_context()
    return ctx.new_page()


def with_page(fn):
    """Decorator helper pattern via context manager usage in callers."""
    settings = load_settings()
    with sync_playwright() as p:
        browser = connect(p, settings)
        page = first_page(browser)
        return fn(page, settings)
