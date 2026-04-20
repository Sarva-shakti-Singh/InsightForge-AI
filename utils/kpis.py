"""KPI extraction & column-type detection helpers."""
from __future__ import annotations
import pandas as pd
import numpy as np
from typing import Dict, List, Optional


def detect_columns(df: pd.DataFrame) -> Dict[str, List[str]]:
    numeric, datetime_cols, categorical = [], [], []
    for c in df.columns:
        s = df[c]
        if pd.api.types.is_numeric_dtype(s):
            numeric.append(c)
        elif pd.api.types.is_datetime64_any_dtype(s):
            datetime_cols.append(c)
        else:
            # try parse to date
            try:
                parsed = pd.to_datetime(s, errors="raise", utc=False)
                if parsed.notna().sum() / max(len(s), 1) > 0.7:
                    datetime_cols.append(c)
                    continue
            except Exception:
                pass
            categorical.append(c)
    return {"numeric": numeric, "datetime": datetime_cols, "categorical": categorical}


def compute_kpis(df: pd.DataFrame) -> Dict[str, float]:
    cols = detect_columns(df)
    kpis: Dict[str, float] = {"rows": float(len(df)), "columns": float(df.shape[1])}
    if cols["numeric"]:
        target = _pick_revenue_col(df, cols["numeric"]) or cols["numeric"][0]
        series = pd.to_numeric(df[target], errors="coerce").dropna()
        if len(series):
            kpis[f"total_{target}"] = float(series.sum())
            kpis[f"avg_{target}"] = float(series.mean())
            kpis[f"max_{target}"] = float(series.max())
            kpis[f"min_{target}"] = float(series.min())
            # growth: compare first vs last quartile
            q = max(1, len(series) // 4)
            first, last = series.iloc[:q].mean(), series.iloc[-q:].mean()
            if first:
                kpis["growth_pct"] = float((last - first) / abs(first) * 100)
    return kpis


def _pick_revenue_col(df: pd.DataFrame, numeric: List[str]) -> Optional[str]:
    priority = ["revenue", "sales", "amount", "total", "price", "income"]
    lc = {c.lower(): c for c in numeric}
    for key in priority:
        for col_l, col in lc.items():
            if key in col_l:
                return col
    return None
