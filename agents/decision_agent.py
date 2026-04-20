"""Decision Recommendation Agent — turns insights into prioritized actions."""
from __future__ import annotations
from typing import List, Dict
import pandas as pd
from .llm_client import LLMClient
from utils.kpis import compute_kpis


class DecisionAgent:
    def __init__(self, llm: LLMClient | None = None):
        self.llm = llm or LLMClient()

    def recommend(self, df: pd.DataFrame, insights: List[str],
                  role: str = "Manager") -> List[Dict]:
        kpis = compute_kpis(df)
        if self.llm.enabled:
            sys = (f"You are a strategic advisor for a {role}. "
                   "From the KPIs and insights, propose 3-5 concrete business actions. "
                   "Each action: a short title, a 1-sentence rationale, and a "
                   "priority (High/Medium/Low). Return strict JSON array with "
                   "fields: title, rationale, priority.")
            import json
            prompt = f"KPIs: {kpis}\n\nInsights:\n- " + "\n- ".join(insights)
            raw = self.llm.chat(sys, prompt, temperature=0.5)
            if raw:
                try:
                    cleaned = raw.strip().lstrip("`").rstrip("`")
                    if cleaned.lower().startswith("json"):
                        cleaned = cleaned[4:].strip()
                    parsed = json.loads(cleaned)
                    if isinstance(parsed, list):
                        return parsed
                except Exception:
                    pass
        return self._heuristic(kpis, role)

    def _heuristic(self, kpis: Dict, role: str) -> List[Dict]:
        recs = []
        g = kpis.get("growth_pct", 0)
        if g < 0:
            recs.append({"title": "Launch retention campaign",
                         "rationale": f"Growth is {g:.1f}% — focus on existing customers first.",
                         "priority": "High"})
            recs.append({"title": "Audit pricing & discounts",
                         "rationale": "Decline often signals pricing-elasticity issues.",
                         "priority": "Medium"})
        else:
            recs.append({"title": "Double down on top segment",
                         "rationale": f"Positive growth ({g:.1f}%) — increase budget on best channel.",
                         "priority": "High"})
            recs.append({"title": "Expand to adjacent regions",
                         "rationale": "Replicate winning playbook in similar markets.",
                         "priority": "Medium"})
        recs.append({"title": "Set up weekly KPI review",
                     "rationale": f"As {role}, monitor revenue, growth, and outliers cadence.",
                     "priority": "Low"})
        return recs
