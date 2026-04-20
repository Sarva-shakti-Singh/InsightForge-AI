"""Insight Generation Agent — explains trends, anomalies and likely root causes."""
from __future__ import annotations
import pandas as pd
import numpy as np
from typing import List
from .llm_client import LLMClient
from utils.kpis import compute_kpis, detect_columns


class InsightAgent:
    def __init__(self, llm: LLMClient | None = None):
        self.llm = llm or LLMClient()

    def generate(self, df: pd.DataFrame) -> List[str]:
        kpis = compute_kpis(df)
        cols = detect_columns(df)
        # heuristic insights always available
        base = self._heuristics(df, kpis, cols)
        if not self.llm.enabled:
            return base
        sys = ("You are a senior business analyst. Produce 4-6 sharp insights "
               "from KPIs and dataset preview. Each insight: one sentence, "
               "with a number, and an implied root cause when possible. "
               "Return as a markdown bullet list.")
        prompt = (f"KPIs: {kpis}\n\nColumn types: {cols}\n\n"
                  f"Sample rows:\n{df.head(6).to_csv(index=False)}")
        out = self.llm.chat(sys, prompt)
        if out:
            return [out]
        return base

    def _heuristics(self, df, kpis, cols) -> List[str]:
        out = []
        if "growth_pct" in kpis:
            g = kpis["growth_pct"]
            direction = "growing" if g > 0 else "declining"
            out.append(f"📈 Trend is **{direction}** at **{g:+.1f}%** comparing "
                       "the first vs last quarter of the dataset.")
        # anomalies
        nums = df.select_dtypes(include=[np.number])
        for c in nums.columns[:3]:
            s = nums[c].dropna()
            if len(s) < 10:
                continue
            mu, sd = s.mean(), s.std()
            outliers = ((s - mu).abs() > 3 * sd).sum()
            if outliers:
                out.append(f"⚠️ Found **{outliers}** outliers in **{c}** "
                           f"(>3σ from mean of {mu:,.1f}).")
        # categorical concentration
        cats = cols.get("categorical", [])
        if cats and nums.shape[1]:
            cat, num = cats[0], nums.columns[0]
            grp = df.groupby(cat)[num].sum().sort_values(ascending=False)
            if len(grp) > 1:
                share = grp.iloc[0] / grp.sum() * 100
                out.append(f"🏆 **{grp.index[0]}** dominates **{cat}** with "
                           f"**{share:.1f}%** of total **{num}**.")
        if not out:
            out.append("No significant signals detected in the current dataset.")
        return out
