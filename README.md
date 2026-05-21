# InsightForge AI Platform

An enterprise-grade, AI-powered Business Intelligence platform built with **Streamlit**.
Upload your data (CSV / Google Sheets / REST API), get automated analytics,
forecasts, AI insights, and recommended business actions — all behind
role-based access (CEO / Manager / Analyst).

---

## ✨ Features

- 🔐 **Multi-user authentication** with bcrypt-hashed passwords
- 👥 **Role-based dashboards** — CEO, Manager, Analyst
- 📊 **Advanced analytics** with Plotly & Matplotlib
- 🤖 **AI Agents**
  - Data Analysis Agent (CSV / SQL understanding)
  - Insight Generation Agent (trend & root-cause explanations)
  - Decision Recommendation Agent (concrete business actions)
  - Forecasting Agent (Prophet + ARIMA fallback)
- 🔌 **Live data sources**: REST API, Google Sheets, CSV upload
- 📈 **Forecasting**: revenue prediction, trend forecasting, risk estimation
- 🗂️ **Dashboards**: Overview · Forecast · Insights · Actions
- 🧠 **Memory system** — stores user queries & interactions per session/user
- 🧱 **Modular architecture** — `agents/`, `dashboards/`, `auth/`, `utils/`, `data/`

---

## 📁 Project Structure

```
insightforge-ai/
├── app.py                       # Streamlit entry point
├── requirements.txt
├── README.md
├── .streamlit/
│   └── config.toml
├── agents/
│   ├── __init__.py
│   ├── llm_client.py            # Unified LLM wrapper (OpenAI / Lovable AI / mock)
│   ├── data_agent.py
│   ├── insight_agent.py
│   ├── decision_agent.py
│   └── forecast_agent.py
├── dashboards/
│   ├── __init__.py
│   ├── overview.py
│   ├── forecast.py
│   ├── insights.py
│   ├── actions.py
│   ├── chat.py
│   ├── export.py
│   ├── alerts.py
│   ├── collaboration.py
│   ├── advanced_analytics.py
│   ├── data_quality.py
│   └── custom.py
├── auth/
│   ├── __init__.py
│   ├── overview.py
│   ├── forecast.py
│   ├── insights.py
│   └── actions.py
├── auth/
│   ├── __init__.py
│   ├── auth_manager.py
│   └── users.yaml               # Demo users (change in production!)
├── data/
│   ├── __init__.py
│   ├── csv_loader.py
│   ├── gsheets_loader.py
│   ├── rest_loader.py
│   └── sample_sales.csv
└── utils/
    ├── __init__.py
    ├── memory.py
    ├── kpis.py
    └── ui.py
```

---

## 🚀 Quick start

```bash
# 1. Clone & enter
git clone <your-repo-url> ai-business-analyst
cd ai-business-analyst

# 2. Create venv
python -m venv .venv
source .venv/bin/activate           # Windows: .venv\Scripts\activate

# 3. Install
pip install -r requirements.txt

# 4. (Optional) configure AI provider — see below
cp .env.example .env  # if you create one

# 5. Run
streamlit run app.py
```

Open http://localhost:8501

### Demo accounts

| Username | Password   | Role    |
|----------|------------|---------|
| ceo      | ceo123     | CEO     |
| manager  | manager123 | Manager |
| analyst  | analyst123 | Analyst |

> ⚠️ **Change these immediately** for any real deployment by editing `auth/users.yaml`
> and re-hashing passwords (`auth/auth_manager.py` includes a `hash_password` helper).

---

## 🤖 Configuring the AI provider

The platform works **out of the box in mock mode** (deterministic, offline insights).
To enable real LLM-powered agents, set environment variables:

**Option A — OpenAI**
```bash
export OPENAI_API_KEY="sk-..."
export AI_MODEL="gpt-4o-mini"
```


If no key is configured, all agents transparently fall back to the built-in
heuristic engine — the app stays fully functional.

---

## 🔌 Data sources

- **CSV upload** — drag & drop in the sidebar
- **REST API** — paste a URL returning JSON (array of objects or `{data: [...]}`)
- **Google Sheets** — paste a public sheet URL, or supply a service-account JSON

---

## 📈 Forecasting

Uses **Prophet** when installed, automatically falls back to **statsmodels ARIMA**,
then to a linear-trend forecaster. Pick a numeric column + date column,
choose horizon, and get prediction intervals + risk score.

---

## 🧠 Memory system

Per-user JSON store (`./.memory/{username}.json`) records:
- Past queries to AI agents
- Datasets loaded
- Generated insights & actions

Available from the sidebar → **Memory**.

---

## 🛡️ Production notes

- Replace `auth/users.yaml` with a real DB (Postgres + SQLAlchemy ready).
- Run behind HTTPS (e.g. Streamlit Community Cloud, Fly.io, or Nginx + Gunicorn-style proxy).
- Set `STREAMLIT_SERVER_ENABLE_CORS=false` and use a proper auth proxy for SSO if needed.
- Rotate `OPENAI_API_KEY`  via your secrets manager.

---

## 📝 License

MIT — do whatever you want, no warranty.

AUTHOR - SARVASHAKTI SINGH
