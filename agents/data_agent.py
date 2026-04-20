"""Data Analysis Agent — profiles the dataset and answers natural-language questions."""
from __future__ import annotations
import pandas as pd
import numpy as np
from typing import Dict, Any
from .llm_client import LLMClient


class DataAgent:
    def __init__(self, llm: LLMClient | None = None):
        self.llm = llm or LLMClient()

    def profile(self, df: pd.DataFrame) -> Dict[str, Any]:
        prof = {
            "shape": df.shape,
            "columns": list(df.columns),
            "dtypes": {c: str(t) for c, t in df.dtypes.items()},
            "null_counts": df.isna().sum().to_dict(),
            "numeric_summary": df.describe(include=[np.number]).to_dict()
                if df.select_dtypes(include=[np.number]).shape[1] else {},
        }
        return prof

    def ask(self, df: pd.DataFrame, question: str) -> str:
        head = df.head(8).to_csv(index=False)
        desc = df.describe(include="all").to_csv()
        sys = ("You are a senior data analyst. Use only the dataset preview "
               "and summary stats provided. Be concise, quote numbers, and "
               "structure your answer with short bullet points.")
        prompt = (f"Question: {question}\n\nDataset head:\n{head}\n\n"
                  f"Summary stats:\n{desc[:2500]}")
        if self.llm.enabled:
            out = self.llm.chat(sys, prompt)
            if out:
                return out
        return self._heuristic_answer(df, question)

    def _heuristic_answer(self, df: pd.DataFrame, q: str) -> str:
        q_l = q.lower()
        nums = df.select_dtypes(include=[np.number])
        lines = [f"Dataset has **{df.shape[0]:,} rows** and **{df.shape[1]} columns**."]
        if "trend" in q_l or "over time" in q_l:
            lines.append("Heuristic trend: comparing first vs last 25% of rows.")
            for c in nums.columns[:3]:
                s = nums[c].dropna()
                if len(s) > 8:
                    q1, q4 = s.iloc[: len(s)//4].mean(), s.iloc[-len(s)//4:].mean()
                    delta = (q4 - q1) / abs(q1) * 100 if q1 else 0
                    lines.append(f"- **{c}**: {delta:+.1f}% change.")
        elif "top" in q_l or "best" in q_l:
            cats = df.select_dtypes(exclude=[np.number])
            if cats.shape[1] and nums.shape[1]:
                cat = cats.columns[0]
                num = nums.columns[0]
                top = df.groupby(cat)[num].sum().sort_values(ascending=False).head(5)
                lines.append(f"Top **{cat}** by total **{num}**:")
                for k, v in top.items():
                    lines.append(f"- {k}: {v:,.0f}")
        else:
            for c in nums.columns[:4]:
                s = nums[c].dropna()
                lines.append(f"- **{c}**: mean={s.mean():,.2f}, "
                             f"min={s.min():,.2f}, max={s.max():,.2f}")
        lines.append("\n_LLM disabled — set `OPENAI_API_KEY`  for richer answers._")
        return "\n".join(lines)
