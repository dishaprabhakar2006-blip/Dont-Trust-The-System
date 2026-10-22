# PROGRESS.md: Don't Trust the System

Last updated: 22 Oct 2026

## Event
- College cybersecurity game, 29 Oct 2026, in the college lab (~60 PCs, so up to 30 teams).
- Each team = 2 players on 2 separate PCs (Analyst + Monitor). Browser only.
- 2-hour slot. Players should be playing ~90 minutes. NO elimination: every team plays all 5 stages at its own pace, winners come from the final leaderboard (score, then time).
- Entry is Rs 75 per team, so the game must be fun, fair and must not crash.
- Story: NovaCorp incident. Hydra trojan is a decoy, the real threat is an insider (hidden account + scheduled task + data upload).

## Setup decisions
- Two repos, kept separate: backend (this repo) and frontend (revathi-r-s/Novacorp, source not pushed yet, only .rar files).
- Run on the lab network from one host laptop (backup: deploy online). Use the in-memory store (FIREBASE_DATABASE_URL empty) unless there is time for Firebase.
- Working solo at ~1-2 hrs/day. Claude (chat) is the coding helper. Antigravity quota is exhausted until 29 Oct, and Codex does not start.

## Backend status (FastAPI, backend/app)
- Done: create team, join team (starts timer), state, mission, actions, results.
- Both roles must answer correctly to unlock the next stage.
- Scoring: 100 points total (stages 10/15/15/20/40). Max 100.
- Timer: per team, starts when player 2 joins. .env has GAME_DURATION_SECONDS=5400 (90 min).
- 27 tests pass: python -m pytest backend/tests
- In progress: team_name field + GET /leaderboard + list_all() (branch: leaderboard).

## Known problems
1. missions.py is a thin quiz: 1 question per role per stage, answers are visible in the evidence. It needs rewriting to match the real game (password puzzle, vault with cross-role clue, phishing email, process/network match, crisis).
2. No limit on wrong guesses (teams can brute-force answers).
3. No frontend connected yet. Plan A: use the Novacorp frontend if source gets pushed. Plan B: build a simple frontend served by FastAPI from this repo.
4. models.py default duration is 1800 and main.py default is 7200. .env overrides both to 5400.

## Next steps (in order)
1. Finish team_name + leaderboard, run tests, merge to main.
2. Rewrite Stage 1 content (several questions per role, decoys, a hint), get it working in /docs with two roles.
3. Basic frontend: join screen, mission screen, answer box, timer, score, big-screen leaderboard page.
4. Rounds 2-5, one at a time, each fully playable before the next.
5. 26-27 Oct: test with friends on 2 PCs, ideally in the lab. Fix places where people get stuck.
6. 28 Oct: fixes, one-page rules sheet, backup laptop ready, seniors' guide.
7. 29 Oct: event.

## Cut list if behind (cut in this order)
Fancy scoring, then hints, then time bonus, then online hosting, then extra decoys. Never cut the test run.

## How to run
```
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --app-dir backend --reload
python -m pytest backend/tests
```
API docs: http://127.0.0.1:8000/docs
For the LAN, run uvicorn with --host 0.0.0.0 and put the frontend origin in FRONTEND_ORIGINS in .env.

## Working rules
- .env is never committed (it is in .gitignore).
- Work on a branch, run the tests after every change, and read the diff before merging.
- Answers and answer keys stay on the server only.
- Do not rename existing routes or response fields without telling the frontend side.

## If I restart in a new chat
Paste this file, then say what step I'm on. Paste the specific files that need changing (models.py, repository.py, main.py, missions.py).
