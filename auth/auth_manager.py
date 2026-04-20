"""Simple file-backed auth with bcrypt-hashed passwords and role mapping."""
from __future__ import annotations
import os
from pathlib import Path
from typing import Optional, Dict
import bcrypt
import yaml

ROLES = ("CEO", "Manager", "Analyst")
USERS_FILE = Path(__file__).parent / "users.yaml"


def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode(), hashed.encode())
    except Exception:
        return False


class AuthManager:
    def __init__(self, users_file: Path = USERS_FILE):
        self.users_file = users_file
        self._ensure_seed_users()

    def _ensure_seed_users(self):
        if self.users_file.exists():
            return
        seed = {
            "users": {
                "ceo": {"password": hash_password("ceo123"), "role": "CEO", "name": "Casey Owens"},
                "manager": {"password": hash_password("manager123"), "role": "Manager", "name": "Morgan Lee"},
                "analyst": {"password": hash_password("analyst123"), "role": "Analyst", "name": "Alex Patel"},
            }
        }
        self.users_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.users_file, "w") as f:
            yaml.safe_dump(seed, f)

    def _load(self) -> Dict:
        with open(self.users_file) as f:
            return yaml.safe_load(f) or {"users": {}}

    def _save(self, data: Dict):
        with open(self.users_file, "w") as f:
            yaml.safe_dump(data, f)

    def login(self, username: str, password: str) -> Optional[Dict]:
        data = self._load()
        u = data["users"].get(username.lower().strip())
        if not u:
            return None
        if not verify_password(password, u["password"]):
            return None
        return {"username": username, "role": u["role"], "name": u.get("name", username)}

    def register(self, username: str, password: str, role: str, name: str = "") -> bool:
        if role not in ROLES:
            return False
        data = self._load()
        if username in data["users"]:
            return False
        data["users"][username] = {
            "password": hash_password(password),
            "role": role,
            "name": name or username,
        }
        self._save(data)
        return True
