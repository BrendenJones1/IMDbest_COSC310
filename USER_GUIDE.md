# IMDbest – User Guide

This guide walks you through setting up the project locally, running the backend and frontend, and using the optional Docker workflow. Follow the steps in order and you will have both services running side by side.

---

## 1. Prerequisites

Install the following tools before cloning the repository:

- **Python 3.10+** (the repo ships with a `requirements.txt`)
- **Node.js 18+** and **npm**
- **Git**
- **Docker** and **Docker Compose** (only needed if you plan to run the backend via containers)

> macOS/Linux: install Python and Node via Homebrew or your distro’s package manager.  
> Windows: install via the official installers (optionally enable WSL for Docker Desktop).

---

## 2. Clone the repository

```bash
git clone https://github.com/BrendenJones1/IMDbest_COSC310.git
cd IMDbest_COSC310
```

If you already cloned it, pull the latest changes:

```bash
git fetch origin
git pull
```

---

## 3. Backend setup (FastAPI)

1. **Create & activate a virtual environment**

   ```bash
   python3 -m venv backend/.venv
   source backend/.venv/bin/activate        # Windows: backend\.venv\Scripts\activate
   ```

2. **Install backend dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Run FastAPI with auto-reload**

   ```bash
   uvicorn backend.main:app --reload
   ```

   The API is now listening on `http://localhost:8000`. Leave this terminal open while the backend runs.

---

## 4. Frontend setup (Vite + React)

1. Install dependencies:

   ```bash
   cd frontend
   npm install
   ```

2. Start the dev server:

   ```bash
   npm run dev
   ```

   Vite will print a URL similar to `http://localhost:5173`. Open it in your browser.  
   Use a **second terminal window** for the frontend so that backend and frontend can run simultaneously.

---

## 5. Running backend & frontend simultaneously

1. Terminal #1 (backend):

   ```bash
   cd IMDbest_COSC310
   source backend/.venv/bin/activate
   uvicorn backend.main:app --reload
   ```

2. Terminal #2 (frontend):

   ```bash
   cd IMDbest_COSC310/frontend
   npm run dev
   ```

With both terminals running, navigate to `http://localhost:5173`, log in with one of the demo accounts, and the frontend will call the FastAPI backend on port `8000`.

---

## 6. Docker workflow (optional)

You can run the backend inside Docker. The provided `docker-compose.yml` targets the backend only; the frontend still runs via `npm run dev`.

1. **Build and start the backend container**

   ```bash
   docker compose up --build backend
   ```

   This launches the API on `http://localhost:8000`. The container name is `cosc310-backend`.

2. **(Optional) Enable live reload**

   In `docker-compose.yml`, uncomment the `volumes` section and the `RELOAD` environment variable, then re-run `docker compose up`. This mounts your working directory inside the container so FastAPI reloads on file changes.

3. **Start the frontend** (outside Docker) using the steps from section 4 in a second terminal.

4. **Stop containers**

   ```bash
   docker compose down
   ```

---

## 7. Useful commands

| Task                               | Command(s)                                                                 |
|------------------------------------|-----------------------------------------------------------------------------|
| Run backend with hot reload        | `uvicorn backend.main:app --reload`                                        |
| Run backend via Docker             | `docker compose up --build backend`                                        |
| Install frontend dependencies      | `cd frontend && npm install`                                               |
| Run frontend dev server            | `cd frontend && npm run dev`                                               |
| Run backend unit tests (example)   | `source backend/.venv/bin/activate && pytest`                              |
| Lint frontend                      | `cd frontend && npm run lint` (if configured)                              |

---

### Demo accounts

Use these logins to explore the app quickly. All passwords are `password`.

| Role  | Email              |
|-------|--------------------|
| Admin | `admin@demo.com`   |
| User  | `elon@demo.com`    |
| User  | `trump@demo.com`   |
| User  | `messi@demo.com`   |

---

You’re ready to build and test features. If you run into issues, check the terminal output for errors, verify both servers are running, and ensure you have the latest dependencies installed. Happy hacking!
