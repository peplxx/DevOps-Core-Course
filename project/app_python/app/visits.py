"""File-backed visit counter with a coarse lock for concurrent requests."""

from __future__ import annotations

import os
import threading
from pathlib import Path

_lock = threading.Lock()


def visits_path() -> Path:
    return Path(os.environ.get("VISITS_FILE", "/data/visits"))


def _read_raw(path: Path) -> int:
    if not path.exists():
        return 0
    try:
        text = path.read_text(encoding="utf-8").strip()
        return int(text) if text else 0
    except (ValueError, OSError):
        return 0


def _write_atomic(path: Path, value: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(str(value), encoding="utf-8")
    tmp.replace(path)


def increment_visits() -> int:
    path = visits_path()
    with _lock:
        n = _read_raw(path) + 1
        _write_atomic(path, n)
        return n


def read_visits() -> int:
    path = visits_path()
    with _lock:
        return _read_raw(path)
