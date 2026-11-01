# Cricket Pitch Analysis (React + FastAPI)

    cricket_pitch_api/
      backend/    your FastAPI app + best.pt (unchanged)
      frontend/   React (Vite) app
      main.py     serves the built React app at / and your backend under /api

## Run (one server)

    # 1. build the React app once (Node 18+)
    cd frontend && npm install && npm run build && cd ..

    # 2. start everything
    pip install -r backend/requirements.txt
    uvicorn main:app --port 8000
    # open http://localhost:8000

## Develop the UI (hot reload)

    uvicorn main:app --port 8000        # terminal 1
    cd frontend && npm run dev          # terminal 2 -> http://localhost:5173 (proxies /api to :8000)
