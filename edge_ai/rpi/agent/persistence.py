"""Persistent session logging with background I/O thread."""

from __future__ import annotations

import json
import queue
import threading
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, Optional


class SessionLogger:
    """Write structured events to logs/session.jsonl asynchronously."""

    def __init__(self, log_dir: Optional[Path] = None) -> None:
        self.log_dir = log_dir or Path(__file__).resolve().parents[1] / "logs"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self._queue: queue.Queue = queue.Queue()
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._worker, daemon=True)
        self._thread.start()

    def log(self, event: str, data: Optional[Dict[str, Any]] = None) -> None:
        """Non‑blocking log entry."""
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": event,
            **(data or {}),
        }
        self._queue.put(entry)

    def stop(self) -> None:
        self._stop.set()
        self._thread.join(timeout=1.0)

    def _worker(self) -> None:
        while not self._stop.is_set():
            try:
                entry = self._queue.get(timeout=0.5)
                with open(self.log_dir / "session.jsonl", "a", encoding="utf-8") as f:
                    f.write(json.dumps(entry) + "\n")
            except queue.Empty:
                continue
            except Exception:
                # Avoid crashing the thread; silently discard on I/O error
                pass
