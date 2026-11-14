from __future__ import annotations

import os
from pathlib import Path

from pydantic import BaseModel, Field


def default_home() -> Path:
    return Path(os.environ.get("AICOMPUTER_HOME", Path.home() / ".aicomputer")).expanduser()


class Settings(BaseModel):
    home: Path = Field(default_factory=default_home)
    cdp_host: str = Field(default_factory=lambda: os.environ.get("CHROME_CDP_HOST", "127.0.0.1"))
    cdp_port: int = Field(default_factory=lambda: int(os.environ.get("CHROME_CDP_PORT", "9222")))
    profile_dir: Path | None = None
    inbox_dir: Path | None = None
    prepared_dir: Path | None = None

    def model_post_init(self, __context: object) -> None:
        if self.profile_dir is None:
            env = os.environ.get("CHROME_PROFILE_DIR")
            self.profile_dir = Path(env).expanduser() if env else self.home / "chrome-profile"
        if self.inbox_dir is None:
            env = os.environ.get("AICOMPUTER_INBOX")
            self.inbox_dir = (
                Path(env).expanduser()
                if env
                else Path(__file__).resolve().parents[2] / "media" / "inbox"
            )
        if self.prepared_dir is None:
            env = os.environ.get("AICOMPUTER_PREPARED")
            self.prepared_dir = (
                Path(env).expanduser()
                if env
                else Path(__file__).resolve().parents[2] / "media" / "prepared"
            )

    @property
    def state_dir(self) -> Path:
        return self.home / "state"

    @property
    def screenshots_dir(self) -> Path:
        return self.home / "screenshots"

    @property
    def logs_dir(self) -> Path:
        return self.home / "logs"

    @property
    def cdp_url(self) -> str:
        return f"http://{self.cdp_host}:{self.cdp_port}"

    def ensure_dirs(self) -> None:
        for path in (
            self.home,
            self.profile_dir,
            self.state_dir,
            self.screenshots_dir,
            self.logs_dir,
            self.inbox_dir,
            self.prepared_dir,
        ):
            assert path is not None
            path.mkdir(parents=True, exist_ok=True)


def load_settings() -> Settings:
    settings = Settings()
    if settings.cdp_host not in {"127.0.0.1", "localhost"}:
        raise RuntimeError(
            f"Refusing CDP host {settings.cdp_host!r}: must be localhost-only."
        )
    settings.ensure_dirs()
    return settings
