# PROGRESS.md: Don't Trust the System

Last updated: 25 Oct 2026 (event is Thursday 29 Oct 2026, 4 days left)

> SPOILER WARNING: sections 6 and 9 contain every answer and the story solution. Keep this repo PRIVATE (GitHub, Settings, Danger Zone, Change visibility). After making it private, check that Render still deploys (reconnect the repo in Render settings if it stops).
## 0. LATEST STATUS (25 Oct 2026, night). Paste this ABOVE section 1.

**Built and playable: Rounds 1 to 5.** `python -m pytest backend/tests -q` gives 50 passed (needs `backend/tests/conftest.py` that sets START_STAGE=1).

### Round 5 "The Crisis" (new)
- Files: `backend/app/stage5.py`, `backend/app/static/stage5_ui.js`, `backend/tests/test_stage5.py`.
- Edits: `models.py` (stage_started_at, outcome), `main.py` (_stage5_total, _stage5_values, countdown and data-lost in _refresh_team_timer, outcome on completion, _refresh_team_timer called first in submit_action), `missions.py` (`MISSIONS[5] = STAGE5_MISSION`), `index.html` (`<div id="dts5" class="hidden">` ABOVE `<div class="grid">`, script tag, window.s5 in poll, DTS5.render, showDone outcomes, DONE timer).
- The glitch reveal (DTS5.reveal) must run when the player CLICKS "Close the case" on the fake SYSTEM SECURED screen, inside clearBtn.onclick. Not when that screen appears.
- Countdown: 8 min (STAGE5_SECONDS=480), 6 min if flag 3:deleted. Server-side, starts when the team first enters stage 5.
- Scoring: 40 points (Analyst 20: a1 7, a2 7, a3 6. Monitor 20: m1 10, m2 10). Wrong insider = half points (3 and 5), no deduction. Time out = DATA LOST: keep points already earned, minus 5, outcome data_lost. Wrong clicks use normal wrong-answer rules (5 in a row lock 30 s).
- Answers (SPOILERS): Analyst disables svc_backup01 and ArchiveIndex (not the look-alike ArchiveIndexer), insider jordan.lee. Monitor blocks row n8443 (203.0.113.77, 61 MB, since 03:07, flat line), insider jordan.lee.
- Insider logic: the rule is printed on screen (on approved leave on 14 Oct but still logged in that day). Analyst's HR table: jordan 13 to 17 Oct, ben 12 to 16, priya 14 to 15. Monitor's 14 Oct login table: only jordan.lee is active while on leave (09:31 opened the Hydra email, 13:07 login).
- Layout: on stages 4 and 5 the page widens, table cells wrap (full text visible), and the red upload bar and countdown stick to the top.

### Lessons from debugging
- The tests read `.env`. Never leave START_STAGE in `.env` (also not in Render). conftest.py forces START_STAGE=1.
- test_all_five_stages must answer jordan.lee for stage 5 questions a3 and m2.
- Python tuples in `_LOGINS` need commas. A missing one crashes stage5.py at import.
- Press Ctrl+F5 after changing HTML or JS. Restart the server after changing Python.

### Decisions
- Keep the 90 minute clock for now. Re-check after timing a senior and friends (105 may be safer).
- Participant briefing is spoiler-free: take notes, 100 points, 1 point per hint, 5 wrong answers lock 30 s, Round 4 needs a phone, clock starts when both join, last round is timed, no searching, highest score wins and faster team breaks ties.

### Come back to these (in this order)
1. Save progress to a file, rejoin option for closed tabs, "Start for everyone" button. (Save and rejoin are NOT cuttable.)
2. QR round: highlight the selected tile, animate swaps and rotation, add a "skip the QR" option (-5 points), make the QR hint cost more.
3. Wrong-answer and lockout messages shown beside the input, big and red, so nobody has to scroll.
4. Green congratulation pop-up after every round (including Round 3) and a finale celebration.
5. Hints on every question (run the no-hint check script).
6. Round 3 rework (clickable inbox, same-feel problem with Round 2).
7. Restyle leaderboard.html, rules sheet, seniors guide, clue audit.
8. Tune Round 5 difficulty after a real playtest (add decoys if too easy).
9. Make the repo private (check Render still deploys), remove START_STAGE everywhere, dry run in the lab (27th, date to be confirmed).
10. Promo message is written. Fill in time, venue, fees, prizes, link and contacts.
## 1. The event
- College cybersecurity puzzle game, 29 Oct 2026, in the college lab. About 25-30 teams, ~60 PCs, Chrome on all PCs, ~16 inch screens, internet available.
- Each team = 2 players on 2 separate PCs (Analyst + Monitor). They sit NEXT TO EACH OTHER, so puzzles should need both players to act, not only hide information.
- 2-hour slot. Each team has its own 90-minute clock that starts when the 2nd player joins (decided: keep 90, do not extend). Content is designed so a typical team finishes in about 75 minutes and the fastest in about 55. NO elimination. Everyone plays all 5 stages.
- Ranking: score first, then fastest finishing time (decided: "Option 1", no speed bonus). Hint costs 1 point, so one hint beats ten minutes of speed. Rules-sheet line: "100 points in total. Each hint costs 1 point. Highest score wins. If tied, the faster team wins."
- Paid entry (Rs 75 per team), so it must feel exciting, scary and fair, and must not crash.
- Phones and internet are allowed (not policed). Seniors walk around. The QR round needs a phone.
- Story: NovaCorp incident. The Hydra trojan is a decoy. The real threat is an insider (jordan.lee) with a hidden account (svc_backup01) and a scheduled task (ArchiveIndex), copying data out.
- Registration form text was written (title "DON'T TRUST THE SYSTEM", teaser, "No coding. No hacking skills. No elimination."). Still to fill in: venue, time, form link, prizes. If the form copy says "90 minutes" it must match the clock.

## 2. People
- Disha: organiser, builds everything alone, first event, beginner at servers and git. Explain step by step in casual language. She pastes code into VS Code and sometimes misses one of several edits, so list edits as a checklist and ask for the pytest output.
- Frontend volunteer: gone, not used. We built our own frontend.
- Tech head: agreed to a fixed IP for the server, port 8000 needs a dry run, will try to be there on the 29th. Not guaranteed to help more. Was asked to test the Render deploy and give feedback.
- Sneha: lab logistics (dry run slot, projector, HDMI, power, lab assistant, seating).

## 3. Decisions made
- Backend (FastAPI) also serves the frontend at /play/, so there is ONE thing to run and no CORS issues.
- Event day: game server on a lab PC with a fixed IP (tech head), Disha's laptop is the backup set up the same way. Prefer the laptop as the main server if the tech head cannot promise Python and the .venv survive a reboot. Players open http://SERVER_IP:8000/play/.
- Render (dont-trust-the-system.onrender.com) is only for the tech head to test. Free tier sleeps (first load up to a minute) and every redeploy wipes all teams.
- Firebase is NOT used (leave FIREBASE_DATABASE_URL empty). Teams are in memory.
- Leaderboard on the projector from Disha's laptop at /play/leaderboard.html. Player screens show only their own score.
- Design rules from Disha's feedback (follow these):
  - Every round must make players do a DIFFERENT kind of thing, not the same read-and-type loop.
  - No typing shell commands. No search box (it removes the reading effort). Click-only File Explorer.
  - Plenty of decoys and longer logs. Players should have to read.
  - A congratulations screen after each round.
  - Hints cost points but must exist on every question.
- Claude (chat) writes the code and Disha pastes it into VS Code. The Claude sandbox can run pure-Python and Node checks but has no FastAPI, pytest or QR library, so Claude cannot run the real pytest suite or scan a real QR. Disha must run pytest and test on real screens.

## 4. How it works (technical)
Repo: dishaprabhakar2006-blip/Dont-Trust-The-System

```
backend/app/
  main.py          routes, timer, scoring engine, attempt lockouts, hints
  models.py        Team model (flags, answered, wrong_attempts, locked_until, hints_used...)
  repository.py    in-memory store (Firebase adapter exists, unused)
  missions.py      Stage 1, Stage 2, Stage 5 (placeholder) content + all mission/asset helper functions
  stage3.py        Stage 3 mission + both fake file systems
  stage4.py        Stage 4 mission, tables, QR tile definitions
  terminal.py      server-side fake file system (Stage 2 data + imports Stage 3). Commands run server side
  assets/          stage4_tile1.png ... stage4_tile6.png (made by tools/make_qr_tiles.py, MUST be committed)
  static/
    index.html     whole game UI (join, intro, mission, explorer, round-cleared screen, timer)
    stage4_ui.js   Round 4 UI: tables, dial lock, order lock, QR tile board
    leaderboard.html
tools/make_qr_tiles.py   makes the 6 tiles and tools/stage4_qr_preview.png (scan the preview, must read KS-4D91)
backend/tests/     test_main.py, test_leaderboard.py, test_repository.py
```

Routes: POST /teams, POST /teams/join, GET /teams/{id}/state, GET /teams/{id}/mission?player_id=, POST /teams/{id}/actions {player_id, question_id, answer}, POST /teams/{id}/hint, POST /teams/{id}/terminal {player_id, command, cwd}, GET /teams/{id}/asset/{asset_id}?player_id=, GET /teams/{id}/results, GET /leaderboard, GET /health. "/" redirects to /play/.

Engine features (all implemented in missions.py and main.py):
- Question: {id, prompt, answers[] (lowercase), points, after (own-role question id), hint}. Optional fields: choices (buttons), pick (answer comes from a table row button), kind "dial" (digits) or "order" (cards), effects.
- effects: {answer: {flag, points, penalty}}. A correct answer can set a flag (stored as "<stage>:<name>" in team.flags), change the points awarded, and subtract a penalty.
- Evidence, tables, table rows, terminal files and assets can be gated by: after (own-role question), flag (shown only after that flag), unless (hidden after that flag), flags_all (assets: all flags needed).
- Players see only unlocked evidence and questions. Answers and hints never leave the server (hints only via /hint).
- Scoring: 100 total. Per role per stage: S1 5/5, S2 7/8, S3 7/8, S4 10/10, S5 20/20. A hint costs 1 point once per question. 5 wrong answers in a row lock that question for 30 s (grows). Score is shared by the team.
- Timer: per team, starts when player 2 joins. GAME_DURATION_SECONDS defaults to 5400 in main.py and models.py.
- START_STAGE in .env makes new teams start at that stage (TESTING ONLY). Remove it before the event. It is never committed because .env is git-ignored, but check Render's environment settings too.
- UI hooks in index.html: round-cleared screen (CLEARED texts for rounds 1-4, round 4 shows a fake "SYSTEM SECURED"), File Explorer (Windows-style table with back/up/path bar, hidden dot-folders look the same as the others, sorted ignoring the dot), choice buttons with confirm pop-up, window.flags for the round-3 clear message, DTS4.render / DTS4.question for Round 4.

## 5. Run it
```
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port 8000
python -m pytest backend/tests -q
```
Game: http://127.0.0.1:8000/play/ (use the laptop's LAN IP on other devices; 0.0.0.0 is not a browsable address). Press Ctrl+F5 after changing HTML or JS. Restart the server after changing Python files, and note a restart wipes all teams.
.env (never committed): GAME_DURATION_SECONDS=5400, other lines empty, no START_STAGE.
Git: work on a branch for risky changes. `git add .`, `git commit -m "..."`, `git push origin <branch>`, merge into main, push main (Render redeploys from main).

## 6. Content status and answers (SPOILERS)

Shared fragments: KS-A7F3 (R1), KS-19C4 (R2), KS-7B20 (R3), KS-4D91 (R4). Kill-switch = KS-A7F3-19C4-7B20-4D91.

**Stage 1 "Briefing: NovaCorp Is Down": DONE, played and liked (~15 min for Disha).**
Password NOVADB02_4471_1410 (server name no hyphen + EMP digits of the FIRST opener of the fake email + incident date DDMM 1410). Analyst a1 password, a2 KS-A7F3 (log line at impossible time 27:00:00). Monitor m1 password, m2 203.0.113.77.

**Stage 2 "The Vault": DONE, Disha played it in 12-13 min (real teams expect 1.3-1.5x).**
Click-only File Explorer, no search. Long logs (about 38 rows) with look-alike times (03:07, 13:07, 23:07, 11:07) and decoy hidden folders (.cache_old sits in the middle of the list). Analyst: a1 banner, a2 svc_backup01, a3 archiveindex (decoded Caesar note, shift 3). Monitor: m1 svc_backup01 (03:07 login from the one IP not in known_networks.txt), m2 0210, m3 3 (shift number in config/scratchpad.txt). Planted clue: the note says ArchiveIndex runs after cleanup.

**Stage 3 "The Curveball": built, tested with scripts, NOT yet played by Disha. Judged the weakest round (see section 7).**
Analyst explores /tmp: a1 .leave_notice.txt, a2 EMP-5120, a3 KS-7B20. Monitor reads the fake email in mail/inbox (sender nov4corp.example vs real novacorp.example, sent 03:20, hours before the 09:14 alert; header IP 203.0.113.77): m1 nov4corp.example, m2 03:20, m3 buttons Keep / Delete (with confirm pop-up).
- Keep: fragment 3 appears for the Monitor, no penalty.
- Delete: team loses 6 points compared with keep (no 3 points for the choice, plus a 3 point penalty), /tmp empties, a red alert shows on the Analyst screen, /var/backups/tmp_snapshot and restore.log appear (24 blocks, 3 FAILED decoys: KS-7B02, KS-7D20, KS-B720, the real one passed its checksum), and /var/log/cleanup_event.log says ArchiveIndex was armed by the cleanup. Idea for Round 5: shorten the countdown if flag "3:deleted" is set.
- Planted clues: leave notice for EMP-5120 (jordan.lee) who still logged in, idx_task.cfg (owner svc_backup01, trigger after_cleanup).

**Stage 4 "The Core Dump": built (redesigned after Disha said the first version was too easy), logic tested with scripts, NOT yet played, QR NOT yet scanned on a real phone.**
Hydra's memory arrives as a QR code cut into 6 tiles (3 across, 2 down, tiles 10x15 squares, 12 px per square), shuffled and flipped upside down per team. Four locks open the tiles:
1. TRACE (tiles 1,2): Monitor m1 = 5050 (external address with sharp regular spikes in the "Last 30 seconds" line; the biggest sender, port 445, is a decoy; 8443 is the flat steady insider stream). Analyst a1 = 3188 (PID owning port 5050; two other processes also started at 09:14), a2 = click End process on svc_updater.exe (row id p3188). Wrong rows: Hydra_Update.exe (quarantined decoy), patch_installer.exe, sysmon_helper.exe (owned by svc_backup01, the insider's process). Sets flag hydra_killed, removes the Hydra rows.
2. HEX (tile 3): Analyst a3 = shadow (header 53 48 41 44 4F 57; Monitor has the hex table).
3. DIAL (tiles 4,5): each player counts rows for the OTHER's dial. Analyst a4 = 5-4-8 (Monitor counts internal/external/ESTABLISHED connections). Monitor m2 = 2-5-3 (Analyst counts processes started 09:14 / owned by svc_ users / owned by avery.park). Both dials needed.
4. ORDER (tile 6): Monitor m3 = c,a,b,d,e (02:30 maintenance login, 03:07 hidden account session, 03:20 fake email, 09:14 quarantine, 13:07 employee on leave logs in). Monitor knows two times, Analyst three.
Then: Monitor m4 = KS-4D91 (scan the rebuilt QR; hint gives the text for 1 point), kill-switch m5 and a5 = KS-A7F3-19C4-7B20-4D91. Points: Analyst 1+3+2+2+2, Monitor 2+2+2+2+2.
Board UI: click tile then another to swap, Rotate selected tile, Scan view (white background, bigger), Shuffle again. Board layout is saved per team in sessionStorage so it survives polling.
Planted clue: after Hydra dies one flat steady line to 203.0.113.77 keeps sending.
Finishing Round 4 shows a green SYSTEM SECURED screen that is a fake win.

**Stage 5 "The Crisis": NOT built. Still the old one-question placeholder ("Who is the insider threat?" answer jordan.lee, 20 points per role).**

## 7. To do, in order
Today is 25 Oct. Time is the main risk.

1. Verify the repo state (Disha may have missed edits). Run `python -m pytest backend/tests -q`. Expected after all Round 4 edits and tests: 48 passed (last confirmed by Disha: 37 passed after Stage 2; Stage 3 tests (41) had failures caused by missing main.py edits, then fixed but not re-confirmed; Stage 4 tests (48) not run). Checklist of Round 4 edits: stage4.py replaced, stage4_ui.js in static/, `<script src="stage4_ui.js">` and `<div id="dts4">` in index.html, DTS4.render(m) and tables in the key line, new question block (choices / pick / kind), renderAssets hides assets whose id starts with "tile", _asset_open has flags_all, public_mission copies kind/digits/cards, main.py passes team.flags to visible_assets and find_asset and run_command and public_mission and records penalty.
2. Run `python tools/make_qr_tiles.py`, scan tools/stage4_qr_preview.png with a phone (must read KS-4D91), commit the six PNGs.
3. Playtest Stage 3 (keep and delete) and Stage 4 with START_STAGE and two browser windows. Time each stage with friends who have not seen it. Targets: R1 12-15 min, R2 15-18, R3 10-14, R4 18-22, R5 10-12. If Round 4 is too hard: reduce to 4 tiles or drop the flipping, or make the QR hint cheaper.
4. Build Stage 5 (design below).
5. Save team progress to a file so a server restart does not wipe teams. NOT cuttable.
6. Rejoin option for closed or frozen tabs (player id + team code). NOT cuttable.
7. Organiser "Start for everyone" button (optional).
8. Rules sheet for participants (include the scoring line and "bring a charged phone"), seniors' guide, clue audit across all stages.
9. Make the repo private, check Render still deploys. Remove START_STAGE from .env and from Render settings.
10. Lab dry run (date to be confirmed by Sneha, planned 27 Oct): port 8000 from another PC, 10-20 PCs playing, projector and HDMI, fixed IP, backup machine set up, QR scans from lab screens, screens look right. No new features after the dry run.
11. 28 Oct: fixes only, backup laptop ready. 29 Oct: event.

Cut list if behind (cut in this order): leaderboard restyle, organiser start button, Round 3 rebuild, extra decoys. Never cut: save-to-file, rejoin, the dry run.

**Round 3 polish (only if time remains after Round 5).** Disha said Round 3 feels like Round 2 again (same explorer, answers just sit in files). Ideas: replace the explorer with a real clickable inbox where buttons like "Show full headers" and "Check sender" each reveal one clue; add a visible 3-minute countdown on the urgent email for pressure; make the Analyst's part need the Monitor's information; decide whether the Delete pop-up should warn about the point loss (it currently only says it cannot be undone).

**Stage 5 design (from Disha's brief).** Right after the fake SYSTEM SECURED screen, the screen glitches and the attacker's message appears: "Thanks for killing Hydra. You just gave me the time I needed." Reveal: Hydra was a decoy, an insider with a hidden account has been copying data out. A short red countdown starts. The pair must act together: the Monitor traces the steady stream (203.0.113.77) and blocks that IP; the Analyst finds the hidden account (svc_backup01) and the "after cleanup" task (ArchiveIndex) and disables both; together they name the insider (jordan.lee, EMP-5120) from clues planted in earlier rounds, preferably chosen from a dropdown of suspects (avery.park, jordan.lee, maria.dsouza, ben.carter, priya.nair, contractor.ray). Outcomes: stop the upload and name the right insider = full win; stop it but name the wrong person = partial score; time runs out = data lost, heavy penalty. Teams that noted the planted clues move fast. Optional: shorter countdown if flag "3:deleted". Keep it click-driven (buttons, dropdown), no typing commands. 40 points total (20 per role).

## 8. Event-day notes
- Setup sheet exists as a Claude Doc ("Don't Trust the System: Event-Day Setup Sheet") with commands, timeline, troubleshooting and rules.
- Server rules: do not restart the server during the event. Never use --reload. One worker only. Keep power and network connected, prefer a wired connection, do not switch networks. Ask the tech head whether lab PCs reset on reboot and whether Python can be installed and stay installed.
- If port 8000 is blocked, try --port 8080 or 80. A hotspot cannot replace the lab network.
- Windows firewall must allow Python on the Private network. Some routers block devices from seeing each other (AP isolation).
- Clock: each team's 90 minutes starts when its second player joins. If a briefing runs 10 minutes before teams join, the last team times out near minute 100 of the 120-minute slot, so tell teams to join promptly.
- Home LAN test passed: /health and /play/ opened on a phone using the laptop's IP.

## 9. Story solution (spoilers)
- Hydra is a decoy: quarantined before it ran. The fake sysadmin email (look-alike domain nov4corp.example, sent 03:20 from 203.0.113.77) pushes teams to delete /tmp, which is evidence, and deleting arms the ArchiveIndex task ("after cleanup").
- Insider: jordan.lee (EMP-5120, IT Support), on approved leave 13 to 17 Oct but opened the Hydra email at 09:31 on 14 Oct and logged in at 13:07. Decoys: avery.park (EMP-4471, first to open the email), maria.dsouza (EMP-3308, approved 02:30 maintenance login), contractor.ray (VPN login at 03:07:30, known VPN pool).
- Hidden account: svc_backup01, created 2026-10-02, no HR request, session opened 03:07:41 from 203.0.113.77 (outside 10.0.4.x and 10.0.9.x). Its process sysmon_helper.exe (PID 1188, port 8443) is the steady 1 KB/s stream that continues after Hydra is killed. Scheduled task ArchiveIndex, trigger after_cleanup, owner svc_backup01.
- Hydra's real process: svc_updater.exe PID 3188, port 5050, server 198.51.100.24 (also appears blocked in earlier firewall logs).

## 10. How to continue in a new chat
Paste this file, say which step of section 7 you are on, and paste the files that need changing (missions.py, main.py, terminal.py, static/index.html, plus stage3.py / stage4.py / stage4_ui.js when relevant). Also paste the latest `python -m pytest backend/tests -q` output.
Style: casual, direct and honest, step by step, break big problems into named parts, explain git and server terms simply, give copy-paste code and exact commands. For big new files give them as downloadable files and list edits to existing files as find/replace with the exact line to find. Say clearly what was tested and what was not (Claude cannot run the real pytest suite, scan a QR code, or see the real browser). Do not claim a puzzle is the right difficulty without Disha's friends' timings.