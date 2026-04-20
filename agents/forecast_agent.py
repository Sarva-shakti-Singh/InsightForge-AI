"""Forecasting Agent — Prophet → ARIMA → linear-trend fallback."""
from __future__ import annotations
import pandas as pd
import numpy as np
from typing import Dict, Any


class ForecastAgent:
    def forecast(self, df: pd.DataFrame, date_col: str, value_col: str,
                 horizon: int = 60) -> Dict[str, Any]:
        ts = df[[date_col, value_col]].dropna().copy()
        ts[date_col] = pd.to_datetime(ts[date_col], errors="coerce")
        ts = ts.dropna().sort_values(date_col)
        ts = ts.groupby(date_col, as_index=False)[value_col].sum()
        if len(ts) < 10:
            raise ValueError("Need at least 10 data points to forecast.")

        method = "linear"
        forecast_df = None
        try:
            from prophet import Prophet  # type: ignore
            m = Prophet(weekly_seasonality=True, yearly_seasonality=True,
                        daily_seasonality=False)
            m.fit(ts.rename(columns={date_col: "ds", value_col: "y"}))
            future = m.make_future_dataframe(periods=horizon)
            fc = m.predict(future)
            forecast_df = fc[["ds", "yhat", "yhat_lower", "yhat_upper"]].rename(
                columns={"ds": date_col, "yhat": "forecast",
                         "yhat_lower": "lower", "yhat_upper": "upper"})
            method = "prophet"
        except Exception:
            try:
                from statsmodels.tsa.arima.model import ARIMA  # type: ignore
                model = ARIMA(ts[value_col].values, order=(2, 1, 2)).fit()
                pred = model.get_forecast(steps=horizon)
                mean = pred.predicted_mean
                ci = pred.conf_int(alpha=0.2)
                future_idx = pd.date_range(ts[date_col].iloc[-1], periods=horizon + 1, freq="D")[1:]
                hist = pd.DataFrame({date_col: ts[date_col],
                                     "forecast": ts[value_col],
                                     "lower": ts[value_col],
                                     "upper": ts[value_col]})
                fut = pd.DataFrame({date_col: future_idx, "forecast": mean,
                                    "lower": ci[:, 0], "upper": ci[:, 1]})
                forecast_df = pd.concat([hist, fut], ignore_index=True)
                method = "arima"
            except Exception:
                # linear trend fallback
                x = np.arange(len(ts))
                coef = np.polyfit(x, ts[value_col].values, 1)
                future_x = np.arange(len(ts), len(ts) + horizon)
                future_y = np.polyval(coef, future_x)
                future_idx = pd.date_range(ts[date_col].iloc[-1], periods=horizon + 1, freq="D")[1:]
                resid_std = (ts[value_col].values - np.polyval(coef, x)).std()
                hist = pd.DataFrame({date_col: ts[date_col],
                                     "forecast": ts[value_col],
                                     "lower": ts[value_col],
                                     "upper": ts[value_col]})
                fut = pd.DataFrame({date_col: future_idx, "forecast": future_y,
                                    "lower": future_y - 1.28 * resid_std,
                                    "upper": future_y + 1.28 * resid_std})
                forecast_df = pd.concat([hist, fut], ignore_index=True)
                method = "linear"

        # risk: coefficient of variation of recent residuals
        recent = ts[value_col].tail(min(60, len(ts)))
        cv = float(recent.std() / max(abs(recent.mean()), 1e-9))
        risk_score = float(min(1.0, cv))
        return {
            "method": method,
            "history": ts,
            "forecast": forecast_df,
            "risk_score": risk_score,
            "horizon": horizon,
            "date_col": date_col,
            "value_col": value_col,
        }
