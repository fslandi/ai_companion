from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

import click

from . import __version__
from . import chrome as chrome_mod
from . import confirm as confirm_mod
from . import reels as reels_mod
from .config import load_settings
from .reels import HumanActionRequired


def _print_json(data: object) -> None:
    click.echo(json.dumps(data, indent=2, ensure_ascii=False, default=str))


@click.group()
@click.version_option(__version__, prog_name="aicomputer")
def main() -> None:
    """AI Computer helpers: Chrome CDP + Instagram Reels prepare/confirm."""


@main.command("doctor")
def doctor() -> None:
    """Check resources, Chrome CDP, and directories."""
    settings = load_settings()
    mem = ""
    try:
        out = subprocess.check_output(["free", "-h"], text=True)
        mem = out.strip()
    except Exception as exc:  # noqa: BLE001
        mem = f"unavailable: {exc}"

    info = chrome_mod.cdp_version(settings)
    report = {
        "version": __version__,
        "home": str(settings.home),
        "profile_dir": str(settings.profile_dir),
        "inbox_dir": str(settings.inbox_dir),
        "cdp_url": settings.cdp_url,
        "cdp_ok": bool(info),
        "cdp_version": info,
        "display": os.environ.get("DISPLAY"),
        "job": confirm_mod.read_job(settings),
        "memory": mem,
        "chrome_bin": shutil.which("google-chrome-stable")
        or shutil.which("google-chrome")
        or shutil.which("chromium")
        or None,
        "codex_bin": shutil.which("codex"),
    }
    _print_json(report)
    if not info:
        click.echo(
            "Hint: start desktop session, then `aicomputer chrome start`",
            err=True,
        )


@main.group("chrome")
def chrome_grp() -> None:
    """Manage the persistent Chrome session."""


@chrome_grp.command("start")
def chrome_start() -> None:
    """Start Chrome with persistent profile + localhost CDP."""
    settings = load_settings()
    info = chrome_mod.start_chrome(settings)
    _print_json({"status": "ok", "cdp": settings.cdp_url, "version": info})


@chrome_grp.command("status")
def chrome_status() -> None:
    settings = load_settings()
    info = chrome_mod.cdp_version(settings)
    _print_json({"cdp": settings.cdp_url, "ok": bool(info), "version": info})


@main.group("reels")
def reels_grp() -> None:
    """Instagram Reels prepare → confirm flow."""


@reels_grp.command("prepare")
@click.option("--video", "video_path", required=True, type=click.Path(path_type=Path))
@click.option("--caption", required=True, type=str)
@click.option("--dry-run", is_flag=True, help="Record job without browser actions.")
def reels_prepare(video_path: Path, caption: str, dry_run: bool) -> None:
    """Stage a Reel and stop before Share. Requires your later confirm."""
    try:
        job = reels_mod.prepare_reel(video_path, caption, dry_run=dry_run)
    except HumanActionRequired as exc:
        click.echo(f"HUMAN_ACTION_REQUIRED: {exc}", err=True)
        raise SystemExit(2) from exc
    _print_json(job)
    click.echo(
        "Stopped before publish. Review screenshot/RDP, then: aicomputer reels confirm",
        err=True,
    )


@reels_grp.command("status")
def reels_status() -> None:
    settings = load_settings()
    job = confirm_mod.read_job(settings)
    _print_json(job or {"status": "none"})


@reels_grp.command("confirm")
@click.option(
    "--i-understand",
    is_flag=True,
    required=True,
    help="Required explicit flag: you reviewed the prepared Reel and approve Share.",
)
def reels_confirm(i_understand: bool) -> None:
    """Publish the prepared Reel after human review."""
    if not i_understand:
        raise SystemExit("Pass --i-understand after reviewing the prepared Reel.")
    try:
        result = reels_mod.confirm_publish()
    except HumanActionRequired as exc:
        click.echo(f"HUMAN_ACTION_REQUIRED: {exc}", err=True)
        raise SystemExit(2) from exc
    _print_json(result)


@reels_grp.command("abort")
def reels_abort() -> None:
    """Clear the prepared job without publishing."""
    _print_json(reels_mod.abort())


@main.command("inbox")
def inbox_list() -> None:
    """List video files in the inbox directory."""
    settings = load_settings()
    files = sorted(
        p for p in settings.inbox_dir.iterdir() if p.is_file() and not p.name.startswith(".")
    )
    _print_json(
        {
            "inbox": str(settings.inbox_dir),
            "files": [{"name": p.name, "path": str(p), "bytes": p.stat().st_size} for p in files],
        }
    )


if __name__ == "__main__":
    main()
