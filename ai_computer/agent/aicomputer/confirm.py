from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import Settings, load_settings


JOB_NAME = "reels_job.json"


def _job_path(settings: Settings) -> Path:
    return settings.state_dir / JOB_NAME


def write_job(data: dict[str, Any], settings: Settings | None = None) -> Path:
    settings = settings or load_settings()
    settings.ensure_dirs()
    payload = {
        **data,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    path = _job_path(settings)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def read_job(settings: Settings | None = None) -> dict[str, Any] | None:
    settings = settings or load_settings()
    path = _job_path(settings)
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def clear_job(settings: Settings | None = None) -> None:
    settings = settings or load_settings()
    path = _job_path(settings)
    if path.exists():
        path.unlink()


def require_prepared(settings: Settings | None = None) -> dict[str, Any]:
    job = read_job(settings)
    if not job:
        raise RuntimeError("No prepared Reels job. Run: aicomputer reels prepare ...")
    if job.get("status") != "awaiting_confirmation":
        raise RuntimeError(
            f"Job status is {job.get('status')!r}, expected 'awaiting_confirmation'."
        )
    return job
