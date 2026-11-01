"""Single entry point: serves the React frontend AND your unchanged backend.

Run from this folder:  uvicorn main:app --port 8000   ->  http://localhost:8000
  /      -> React build (frontend/dist)
  /api/* -> your backend/app.py (e.g. /api/predict, /api/docs)
"""
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(ROOT, "backend")
DIST = os.path.join(ROOT, "frontend", "dist")

# app.py loads "best.pt" by relative path, so run with backend/ as the cwd.
os.chdir(BACKEND_DIR)
sys.path.insert(0, BACKEND_DIR)

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from app import app as backend_app  # backend/app.py, unmodified

app = FastAPI(title="Cricket Pitch Analysis")
app.mount("/api", backend_app)

if os.path.isdir(DIST):
    app.mount("/", StaticFiles(directory=DIST, html=True), name="frontend")
else:
    @app.get("/", response_class=HTMLResponse)
    def not_built():
        return ("<h2>Frontend not built yet</h2>"
                "<pre>cd frontend\nnpm install\nnpm run build</pre>"
                "<p>Then restart this server. The API is already live at <a href='/api/docs'>/api/docs</a>.</p>")
