"""Load JSON from a REST endpoint into a DataFrame."""
from __future__ import annotations
import pandas as pd
import requests
from typing import Optional, Dict


def load_rest(url: str, headers: Optional[Dict[str, str]] = None,
              json_path: Optional[str] = None) -> pd.DataFrame:
    r = requests.get(url, headers=headers or {}, timeout=30)
    r.raise_for_status()
    data = r.json()
    if json_path:
        for key in json_path.split("."):
            data = data[key]
    if isinstance(data, dict):
        # try common keys
        for k in ("data", "results", "items", "records"):
            if k in data and isinstance(data[k], list):
                data = data[k]
                break
        else:
            data = [data]
    return pd.DataFrame(data)
