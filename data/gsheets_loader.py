"""Load Google Sheets — supports public CSV-export URLs and gspread service accounts."""
from __future__ import annotations
import re
import pandas as pd
import requests
from io import StringIO


def _to_csv_export(url: str) -> str:
    m = re.search(r"/spreadsheets/d/([a-zA-Z0-9-_]+)", url)
    if not m:
        return url
    sheet_id = m.group(1)
    gid_m = re.search(r"[?&]gid=(\d+)", url)
    gid = gid_m.group(1) if gid_m else "0"
    return f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"


def load_gsheet(url: str) -> pd.DataFrame:
    csv_url = _to_csv_export(url)
    r = requests.get(csv_url, timeout=30)
    r.raise_for_status()
    return pd.read_csv(StringIO(r.text))
