# CDM2026 — Live API + Frontend

Run locally (virtualenv recommended):

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python live_api.py
```

Deploy:
- Backend: Render (see README_DEPLOY.md)
- Frontend: Netlify (serve `index.html`, set `meta[name="api-endpoint"]` to backend URL)

Files added:
- `api.py`, `fifa_scraper.py`, `odds.py`, `placeholders.py`, `utils.py`, `live_api.py`
