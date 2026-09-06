# AeroGuard AI Production Starter

This package contains a deployable starter:
- responsive public dashboard
- IMD WIS2 station and observation connectors
- source/timestamp attribution
- FastAPI proxy for production hosting
- clearly labelled anomaly screening

Run backend:
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload

The current anomaly endpoint is only a starter screening rule. A validated production detector should be trained on historical station observations and combine temporal and spatial features.
