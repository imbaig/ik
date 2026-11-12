"""Persistent admission limits for the explicitly public grading deployment."""

import sqlite3
from datetime import UTC, datetime
from pathlib import Path

from music_store.application_contracts import ActionKind, DemoLimitReached


class DemoQuota:
    """Atomic action counts survive restarts; this is NOT a dollar-spend meter."""

    def __init__(self, path, *, daily=60, total=300):
        if not 1 <= daily <= total <= 1000:
            raise ValueError("Public demo requires 1 <= daily <= total <= 1000")
        self.path, self.daily, self.total = Path(path), daily, total
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.path) as db:
            db.execute(
                "CREATE TABLE IF NOT EXISTS usage (day TEXT PRIMARY KEY, actions INTEGER NOT NULL)"
            )

    def reserve(self):
        day = datetime.now(UTC).date().isoformat()
        with sqlite3.connect(self.path, timeout=5) as db:
            db.execute("BEGIN IMMEDIATE")
            today = db.execute("SELECT actions FROM usage WHERE day=?", (day,)).fetchone()
            total = db.execute("SELECT COALESCE(SUM(actions),0) FROM usage").fetchone()[0]
            if (today[0] if today else 0) >= self.daily or total >= self.total:
                return False
            db.execute(
                "INSERT INTO usage VALUES (?,1) ON CONFLICT(day) DO UPDATE SET actions=actions+1",
                (day,),
            )
            return True


class LimitedApplication:
    def __init__(self, service, quota):
        self.service, self.quota = service, quota

    def new_session(self):
        return self.service.new_session()

    def close(self, handle):
        return self.service.close(handle)

    def reset(self, handle):
        return self.service.reset(handle)

    def dispatch(self, handle, action):
        # Cancel/reset must remain usable without a paid provider call.
        if action.kind != ActionKind.CANCEL_VERIFICATION and not self.quota.reserve():
            raise DemoLimitReached(
                "This public demo has reached its usage limit. Please try later."
            )
        return self.service.dispatch(handle, action)
