import json
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from garminconnect import Garmin, GarminConnectTooManyRequestsError

from passada import config


def connect(token_dir: Path = config.TOKEN_DIR) -> Garmin:
    client = Garmin()
    client.login(str(token_dir))
    return client


@dataclass
class RawStore:
    root: Path
    pause_seconds: float = config.PAUSE_SECONDS
    retry_wait_seconds: float = config.RETRY_WAIT_SECONDS
    max_attempts: int = config.MAX_ATTEMPTS
    sleep: Callable[[float], None] = time.sleep
    counters: dict[str, int] = field(default_factory=lambda: {"fetched": 0, "cached": 0, "failed": 0})

    def path(self, relative: str) -> Path:
        return self.root / relative

    def read(self, relative: str) -> Any:
        target = self.path(relative)
        return json.loads(target.read_text()) if target.exists() else None

    def fetch(self, relative: str, call: Callable[[], Any], refresh: bool = False) -> Any:
        target = self.path(relative)
        if target.exists() and not refresh:
            self.counters["cached"] += 1
            return json.loads(target.read_text())
        payload = self._call_with_retry(relative, call)
        if payload is None:
            return self.read(relative)
        self._write(target, payload)
        self.counters["fetched"] += 1
        self.sleep(self.pause_seconds)
        return payload

    def _call_with_retry(self, relative: str, call: Callable[[], Any]) -> Any:
        for attempt in range(1, self.max_attempts + 1):
            try:
                return call()
            except GarminConnectTooManyRequestsError:
                print(f"429 on {relative}, waiting {self.retry_wait_seconds}s (attempt {attempt})", flush=True)
                self.sleep(self.retry_wait_seconds)
            except Exception as error:
                print(f"failed {relative}: {type(error).__name__}: {str(error)[:200]}", flush=True)
                break
        self.counters["failed"] += 1
        return None

    def _write(self, target: Path, payload: Any) -> None:
        target.parent.mkdir(parents=True, exist_ok=True)
        partial = target.with_name(target.name + ".part")
        partial.write_text(json.dumps(payload, default=str))
        partial.replace(target)
