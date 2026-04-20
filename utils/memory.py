"""Lightweight per-user JSON memory store."""
from __future__ import annotations
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

MEM_DIR = Path(".memory")


class Memory:
    def __init__(self, username: str):
        MEM_DIR.mkdir(exist_ok=True)
        self.path = MEM_DIR / f"{username}.json"
        if not self.path.exists():
            self.path.write_text(json.dumps({"events": []}))

    def _load(self) -> Dict[str, Any]:
        try:
            return json.loads(self.path.read_text())
        except Exception:
            return {"events": []}

    def _save(self, data: Dict[str, Any]):
        self.path.write_text(json.dumps(data, indent=2, default=str))

    def add(self, kind: str, payload: Dict[str, Any]):
        data = self._load()
        data["events"].append({
            "ts": datetime.utcnow().isoformat(),
            "kind": kind,
            "payload": payload,
        })
        # cap to last 200 events
        data["events"] = data["events"][-200:]
        self._save(data)

    def recent(self, kind: str | None = None, limit: int = 20) -> List[Dict[str, Any]]:
        data = self._load()
        events = data["events"]
        if kind:
            events = [e for e in events if e["kind"] == kind]
        return list(reversed(events[-limit:]))

    def clear(self):
        self._save({"events": []})
