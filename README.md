# COSC310

## Docker Setup

1. Install [Docker Desktop](https://www.docker.com/products/docker-desktop/) and ensure the daemon is running.
2. From the project root build the containers:
   ```terminal
   docker compose build
   ```
3. Start the stack:
   ```terminal
   docker compose up
   ```
4. Frontend available at http://localhost:3000, backend API at http://localhost:8000.
5. Stop the stack with `Ctrl+C` or run `docker compose down`.

If you change backend dependencies, update `requirements.txt` and re-run `docker compose build backend`.

## Local (non-Docker) Setup

### Terminal 1 – backend

1. `cd backend`
2. `python3 -m venv .venv`
3. `source .venv/bin/activate`
4. `pip install -r ../requirements.txt`
5. `uvicorn backend.main:app --reload`

Backend runs at http://localhost:8000

### Terminal 2 – frontend

1. `cd frontend`
2. `npm install`
3. `npm run dev `

Frontend dev server runs at http://localhost:5173 (or the host/port Vite prints).
