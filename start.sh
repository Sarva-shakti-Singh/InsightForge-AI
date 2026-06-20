#!/usr/bin/env bash
set -e

# If a GOOGLE_SERVICE_ACCOUNT_JSON env var exists, write it to a temporary file
if [ -n "$GOOGLE_SERVICE_ACCOUNT_JSON" ]; then
  echo "$GOOGLE_SERVICE_ACCOUNT_JSON" > /tmp/gcp_sa.json
  export GOOGLE_APPLICATION_CREDENTIALS=/tmp/gcp_sa.json
fi

# Ensure we have dependencies installed (Render usually runs buildCommand separately)
pip install -r requirements.txt

# Start Streamlit on the port Render provides
streamlit run app.py --server.port $PORT --server.address 0.0.0.0 --server.enableCORS false
