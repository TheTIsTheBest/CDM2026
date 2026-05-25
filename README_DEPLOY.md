Deployment notes — Render (backend) + Netlify (frontend)

1) Backend (Render)
- Ensure the repository is connected to Render (or push this folder to a Git repo and link it).
- Render will detect Python when `requirements.txt` is present. The `Procfile` starts Gunicorn:

  web: gunicorn live_api:app --bind 0.0.0.0:$PORT

- Environment: no special vars required. Render will set `PORT`. To enable Flask debug locally set `FLASK_DEBUG=1`.

2) Frontend (Netlify)
- The frontend is the static `index.html` in this folder. Netlify serves static files directly.
- Update the API endpoint meta tag in `index.html` to point to the deployed Render URL. Example:

  <meta name="api-endpoint" content="https://your-render-service.onrender.com/api/live.json">

- Build & deploy on Netlify (drag & drop or connect repo). After deploy, the static site will fetch live data from the Render backend.

3) Notes & next steps
- Odds provider: currently the backend provides estimated odds. To integrate a real odds API, add credentials and implement a fetch in `live_api.py`.
- If you want the backend and frontend on the same domain, consider deploying the API as a subdomain or proxying requests.
