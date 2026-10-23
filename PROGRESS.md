# PROGRESS.md: Don't Trust the System

Last updated: 23 Oct 2026 (event is on 29 Oct 2026)

> SPOILER WARNING: section 9 contains the story solution. Keep this repo PRIVATE (GitHub, Settings, Danger Zone, Change visibility) before the event, because missions.py also holds every answer.

## 1. The event
- College cybersecurity puzzle game, 29 Oct 2026, in the college lab. About 25-30 teams, ~60 PCs, Chrome on all PCs, ~16 inch screens, internet available.
- Each team = 2 players on 2 separate PCs (Analyst + Monitor). They sit NEXT TO EACH OTHER (cannot be separated), so puzzles should need both players to act, not only hide information.
- 2-hour slot. Each team has its own 90-minute clock that starts when the 2nd player joins. NO elimination. Everyone plays all 5 stages. Ranking: score first, then fastest finishing time. Winners announced when every team is Finished or Time up.
- Paid entry (Rs 75 per team), so it must feel exciting, scary and fair, and must not crash.
- Phones and internet are allowed (not policed). Seniors walk around. The game is designed so googling does not help much.
- Story: NovaCorp incident. The Hydra trojan is a decoy. The real threat is an insider with a hidden account and a scheduled task, copying data out.

## 2. People
- Disha (organiser, building everything alone). First time organising an event, a beginner at servers and git, so explain step by step in casual language.
- Frontend volunteer: gone on a trip, not available. Her repo (revathi-r-s/Novacorp) is NOT used. We built our own frontend.
- Tech head: agreed to a fixed IP for the server, said port 8000 needs a dry run, will try to be there on the 29th. Not guaranteed to help more.
- Sneha: handles lab logistics (dry run slot, projector, HDMI cable, power socket, lab assistant, seating).

## 3. Decisions made
- Backend (FastAPI) also serves the frontend at /play/, so there is ONE thing to run and no CORS issues.
- Event day: the game server runs on a LAB PC on the lab network (tech head says it won't fail and gives it a fixed IP). Disha's laptop is the backup, set up the same way. Players open http://SERVER_IP:8000/play/.
- Online hosting is NOT the plan. Render is used only to let the tech head test (dont-trust-the-system.onrender.com). The free Render server sleeps and forgets teams.
- Firebase is NOT used (leave FIREBASE_DATABASE_URL empty). Teams are kept in memory. A save-to-file feature is planned so a restart does not wipe teams.
- Leaderboard is shown on the projector from Disha's laptop (HDMI), opened at /play/leaderboard.html.
- Antigravity quota is used up and Codex does not start. Claude (chat) writes the code and Disha pastes it into VS Code.

## 4. How it works (technical)
- Repo: dishaprabhakar2006-blip/Dont-Trust-The-System (backend/app/main.py, missions.py, models.py, repository.py, static/index.html, static/leaderboard.html, backend/tests/).
- Routes: POST /teams, POST /teams/join, GET /teams/{id}/state, GET /teams/{id}/mission?player_id=, POST /teams/{id}/actions {player_id, question_id, answer}, POST /teams/{id}/hint, GET /teams/{id}/results, GET /leaderboard, GET /health.
- missions.py format: each stage has Analyst and Monitor roles, each with evidence lines (each can unlock after a question id) and a list of questions {id, prompt, answers[], points, after, hint}. Stages 4 and 5 are still the old one-question format, converted by a loop at the bottom of missions.py.
- Scoring: 100 points total (stage points 10/15/15/20/40). A hint costs 1 point, once per question, from the team total. 5 wrong answers in a row cause a 30 second lockout (grows). Team score is shared by both players.
- Frontend (static/index.html): story intro ("BREACH DETECTED"), join/create screens, waiting screen, mission screen with evidence and questions, notes box, timer, score. It polls every 3 seconds. Each browser tab is one player (sessionStorage). Do not duplicate a tab.
- Tests: python -m pytest backend/tests (all pass as of the last run).

## 5. Run it
```
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port 8000
```
Game: http://127.0.0.1:8000/play/  Leaderboard: http://127.0.0.1:8000/play/leaderboard.html
.env (never committed): GAME_DURATION_SECONDS=5400, other lines empty.
Render redeploys automatically on every git push to main. Git routine: git add . then git commit -m "message" then git push origin main. Work on a branch for risky changes.

## 6. Content status
- Stage 1 "Briefing: NovaCorp Is Down": DONE, 4 questions, played and liked. Clearer password wording applied.
- Stage 2 "The Vault": DONE (cross-partner answer, Caesar cipher), played correctly.
- Stage 3 "The Phish": written (fake email, domain and timestamp checks, keep-or-delete decision). Needs a real play-through. The "delete files costs integrity" path is NOT built.
- Stage 4 "Hunt the Hydra": NOT written (design in section 9).
- Stage 5 "The Crisis": NOT written (design in section 9).

## 7. To do, in order
1. Test the real LAN setup at home (laptop server, phone on same Wi-Fi, open /health then /play/). NOT DONE YET.
2. Make the repo private.
3. Build the reusable file explorer and fake terminal (ls, cat, grep, ps, netstat) in the frontend. Convert Stage 2 to use it.
4. Make Stage 3 interactive (clickable email and buttons, delete-or-keep with a penalty path).
5. Write Stage 4: process list on one screen, network connections on the other, match by port, kill the real process, assemble the kill-switch from 4 fragments, then the fake "SYSTEM SECURED" screen.
6. Write Stage 5: glitch reveal, red countdown, block the IP, disable the account and the task, name the insider. Scoring: full win, partial (wrong insider), heavy penalty on timeout.
7. Add an organiser "Start for everyone" button.
8. Save team progress to a file so a server restart does not wipe teams.
9. Add a rejoin option for closed tabs.
10. Restyle leaderboard.html to match the red breach theme.
11. Rules sheet for participants, and a clue audit across all stages.
12. Dry run in the lab on the 27th (date to be confirmed by Sneha): port 8000 from another PC, 10-20 PCs playing, projector and HDMI, fixed IP, backup machine set up, screens look right. No new features after the dry run.

## 8. Event-day notes
- The event-day setup sheet (Claude Doc, "Don't Trust the System: Event-Day Setup Sheet") has the commands, laptop settings, timeline, troubleshooting table and rules.
- Server rules: do not restart the server during the event. Keep power and network connected. Use a wired connection if possible. Do not switch networks. Ask the tech head if lab PCs reset on reboot, and whether Python can be installed and stay installed.
- If port 8000 is blocked, try --port 8080 or 80.
- A hotspot cannot replace the lab network. The game needs a local network, not internet.

## 9. Story solution (spoilers, keep private)
- Hydra is a decoy: quarantined before it ran. The fake sysadmin email (look-alike domain, sent at 03:20) pushes teams to delete /tmp, which is evidence.
- Insider: jordan.lee (EMP-5120), who was on leave (13 to 17 Oct) but opened the Hydra email on 14 Oct. Decoys: avery.park (EMP-4471), maria.dsouza (EMP-3308, approved maintenance login).
- Hidden account: svc_backup01, created 02 Oct, logged in at 03:07 from 203.0.113.77 (outside 10.0.4.x). Scheduled task: ArchiveIndex, trigger "after cleanup". The steady outgoing data stream continues after Hydra is killed.
- Stage 4 idea: process list (Analyst) vs network connections (Monitor), match by port to find the real Hydra process among decoys, 4th fragment hidden as hex or base64, combine fragments into the kill-switch.
- Stage 5 idea: Monitor traces the steady outgoing stream and blocks the IP, Analyst finds the hidden account and task (crontab, users) and disables both, together they name the insider from earlier clues.

## 10. How to continue in a new chat
Paste this file, then say which step you are on. Paste the files that need changing (missions.py, main.py, static/index.html). Style: casual, direct and honest, step by step, break big problems into named parts, explain git and server terms simply, give copy-paste code and exact commands.