# Don't Trust the System

Initial FastAPI backend scaffold for the browser-based cybersecurity investigation game.

## Requirements

- Python 3.10 or newer
- Windows PowerShell

## Setup

Run these commands from the project root (`C:\Dont-Trust-The-System`):

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If PowerShell blocks activation, allow it for the current terminal session with:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

## Run the API

From the project root, start the development server with:

```powershell
python -m uvicorn app.main:app --app-dir backend --reload
```

The API is available at <http://127.0.0.1:8000>. Interactive API documentation is at <http://127.0.0.1:8000/docs>.

## Run with Docker

Install Docker Desktop (or Docker Engine with the Compose plugin), then run these commands from the project root:

```powershell
docker compose up --build -d
docker compose ps
```

Open <http://localhost:8000/play/> on the Docker host. The service listens on all container interfaces and publishes port `8000` on the host, so devices on the same trusted LAN can also connect. Find the host's LAN IPv4 address with `ipconfig`, then open `http://HOST_IP:8000/play/` on another device (replace `HOST_IP` with that address). The API is available at `/docs`, and its health endpoint is `/health`.

To publish a different host port, set `PORT` in `.env` (for example, `PORT=8080`), then connect using that port. Docker publishes the port on all host interfaces; allow it through Windows Firewall only on a trusted **Private network**. Do not expose this development/demo server to the public internet.

The container uses the in-memory repository by default, so data is lost when it restarts. To configure Firebase, set `FIREBASE_DATABASE_URL` and `FIREBASE_SERVICE_ACCOUNT_PATH=/run/credentials/firebase.json` in `.env`, then place the service-account JSON at `credentials/firebase.json` on the host. The `credentials` directory is mounted read-only and excluded from the image. Alternatively, configure Application Default Credentials and `GOOGLE_APPLICATION_CREDENTIALS` to a path available inside the container. For a Firebase emulator running on the Docker host, use `host.docker.internal` in `FIREBASE_DATABASE_EMULATOR_HOST`.

When a separate frontend on the LAN calls the API from a browser, add its exact origin (including scheme and port) to `FRONTEND_ORIGINS` in `.env`. The same-origin `/play/` page does not need an additional CORS origin.

Stop the container with `docker compose down`; view logs with `docker compose logs -f app`.

## Two-device LAN demo

To let a frontend on another device on the same trusted Wi-Fi reach the backend, run Uvicorn bound to all network interfaces from the project root:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port 8000 --reload
```

On the host Windows computer, run `ipconfig` and find the **IPv4 Address** under the active Wi-Fi adapter. Use that address as `HOST_IP` (not `127.0.0.1`). The frontend should use `http://HOST_IP:8000` as its API base URL, replacing `HOST_IP` with that IPv4 address.

The browser origin serving the frontend must be listed in `FRONTEND_ORIGINS`. Set it to the frontend's actual origin, including scheme, host, and port. Once the frontend framework and its development port are known, configure one or more comma-separated origins in the root `.env` file, for example the localhost and host-IP versions of that same origin. The backend allows localhost origins on any port for local development. It does not allow arbitrary origins, and CORS credentials are disabled.

Windows Firewall may prompt to allow Python/Uvicorn. Allow it only on a trusted **Private network** if needed. Both devices must be on the same Wi-Fi/LAN; keep the firewall rule off Public networks.

## Run tests

From the project root:

```powershell
python -m pytest backend/tests
```

## Initial endpoints

- `GET /` returns a welcome message.
- `GET /health` returns `{"status": "healthy"}`.

`.env.example` documents placeholder local settings. Copy it to `.env` only when you need local configuration; never put real credentials in the example file or commit a `.env` file.

## Firebase Realtime Database

Firebase is optional for local development and tests. If `FIREBASE_DATABASE_URL` is unset or empty, the API uses its thread-safe in-memory repository. Data in that mode is cleared when the server stops.

To use Firebase:

1. Create a Firebase project and a Realtime Database. Copy the database URL from the Firebase console.
2. Install dependencies with `python -m pip install -r requirements.txt` (this installs the Firebase Admin SDK).
3. Set `FIREBASE_DATABASE_URL` to the Realtime Database URL. For local service-account credentials, set `FIREBASE_SERVICE_ACCOUNT_PATH` to the JSON file path. Alternatively, configure Application Default Credentials with `GOOGLE_APPLICATION_CREDENTIALS` or a service identity provided by the runtime.
4. Start the API as described above. The backend stores team records under `teams/` and join-code indexes under `join_codes/`. Firebase transactions protect team joins and mission submissions from concurrent updates.

PowerShell example using a local service account file:

```powershell
$env:FIREBASE_DATABASE_URL = "https://YOUR-PROJECT-default-rtdb.firebaseio.com"
$env:FIREBASE_SERVICE_ACCOUNT_PATH = "C:\path\outside\this\repo\firebase-service-account.json"
python -m uvicorn app.main:app --app-dir backend --reload
```

For the Firebase Emulator Suite, also set `FIREBASE_DATABASE_EMULATOR_HOST` (for example, `127.0.0.1:9000`). The emulator does not require a service-account file. Keep service-account JSON outside the repository; `.gitignore` excludes common Firebase credential filenames, `.env`, and virtual environments. Never put credential contents in `.env.example` or source code.

Required Firebase setting: `FIREBASE_DATABASE_URL`. Optional settings: `FIREBASE_SERVICE_ACCOUNT_PATH`, `GOOGLE_APPLICATION_CREDENTIALS`, and `FIREBASE_DATABASE_EMULATOR_HOST`. Leave the database URL unset to run without Firebase.

## Scoring and game timer

Each correct Analyst or Monitor answer awards **100 points**. Each role can earn points only once for its action in a stage; both role actions are required to complete a stage. Completing all five stages marks the game `completed`, for a maximum score of 1,000 points. The backend ignores any client-supplied score or stage.

`GAME_DURATION_SECONDS` sets the game duration (default `1800`, or 30 minutes). The shared timer starts when the second player joins. Both players receive the same persisted `started_at`, deadline, elapsed time, and remaining time from team state. When the deadline passes, the team becomes `expired`; further mission reads and submissions are rejected, and no more points or stage progress are awarded. Timer checks use server UTC time.

`GET /teams/{team_id}/state` includes score, completed stages, game status, and timer fields. `POST /teams/{team_id}/actions` returns points awarded and updated team progress. `GET /teams/{team_id}/results` returns the score, completed stages, final status, and timer summary; its `final` field is true after completion or expiry.
