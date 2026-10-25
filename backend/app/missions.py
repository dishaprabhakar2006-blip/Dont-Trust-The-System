"""Server-authored mission content and answer keys.

Answers and hints never leave the server except hints, which are released
only through the /hint endpoint. All answers must be lowercase.
"""

from backend.app.stage3 import MISSION as STAGE3_MISSION
from backend.app.stage4 import MISSION as STAGE4_MISSION, ASSETS as STAGE4_ASSETS

MISSIONS = {
    1: {
        "title": "Briefing: NovaCorp Is Down",
        "roles": {
            "Analyst": {
                "instructions": (
                    "NovaCorp's admin console is locked. You have the incident report "
                    "and IT policy. Your partner has the employee records. Talk to each other!"
                ),
                "evidence": [
                    {"text": "SYSTEM BANNER: 'Hydra trojan confirmed. No further action needed.'", "after": None},
                    {"text": "INCIDENT REPORT: On 14 Oct 2026 the Hydra alert fired on server NOVA-DB02 after a fake 'security update' email.", "after": None},
                    {"text": "IT POLICY (current): Admin password = 3 parts joined by underscores. PART 1: the affected server's name in capitals, hyphen removed. "
                    "PART 2: the employee ID digits of the FIRST person to open the fake email."
                    " PART 3: the incident date as DDMM.", "after": None},
                    {"text": "IT POLICY (retired 2024): Admin password = company name + year.", "after": None},
                    {"text": "FILES: /logs/auth.log  /logs/backup.log  /home/.cache_old (hidden)", "after": "a1"},
                    {"text": "auth.log 09:02:11 login ok avery.park 10.0.4.21", "after": "a1"},
                    {"text": "auth.log 09:20:55 login ok jordan.lee 10.0.4.35", "after": "a1"},
                    {"text": "auth.log 02:30:00 login ok maria.dsouza 10.0.4.50 (maintenance window)", "after": "a1"},
                    {"text": "auth.log 27:00:00 session opened from 203.0.113.77 note=KS-A7F3", "after": "a1"},
                    {"text": "auth.log 10:05:30 login ok avery.park 10.0.4.21", "after": "a1"},
                    {"text": "backup.log 09:41:17 nightly backup ok", "after": "a1"},
                ],
                "questions": [
                    {
                        "id": "a1",
                        "prompt": "Enter the admin password.",
                        "answers": ["novadb02_4471_1410"],
                        "points": 2,
                        "after": None,
                        "hint": "You have the server name and date. The employee ID is on your partner's screen.",
                    },
                    {
                        "id": "a2",
                        "prompt": "Find the log entry that doesn't belong. What kill-switch fragment is in it?",
                        "answers": ["ks-a7f3"],
                        "points": 3,
                        "after": "a1",
                        "hint": "Look for a timestamp that cannot exist on a clock.",
                    },
                ],
            },
            "Monitor": {
                "instructions": (
                    "You have the employee records and (after login) the live dashboard. "
                    "Your partner has the password format."
                ),
                "evidence": [
                    {"text": "SYSTEM BANNER: 'All accounts verified. Threat contained.'", "after": None},
                    {"text": "MAIL LOG: Hydra email opened 09:12 by avery.park (EMP-4471).", "after": None},
                    {"text": "MAIL LOG: Same email opened 09:31 by jordan.lee (EMP-5120).", "after": None},
                    {"text": "ROSTER: maria.dsouza (EMP-3308) was offline.", "after": None},
                    {"text": "DASHBOARD USER LIST: avery.park, jordan.lee, maria.dsouza, svc_backup01", "after": "m1"},
                    {"text": "ALERT 09:14 Hydra_Update quarantined, no outbound connection.", "after": "m1"},
                    {"text": "ALERT 27:00:00 unusual session source 203.0.113.77", "after": "m1"},
                    {"text": "ALERT 02:30 maintenance login, maria.dsouza, approved.", "after": "m1"},
                ],
                "questions": [
                    {
                        "id": "m1",
                        "prompt": "Enter the admin password.",
                        "answers": ["novadb02_4471_1410"],
                        "points": 2,
                        "after": None,
                        "hint": "You have the employee ID of the FIRST opener. Ask your partner for the format.",
                    },
                    {
                        "id": "m2",
                        "prompt": "Which IP is behind the alert with the impossible timestamp?",
                        "answers": ["203.0.113.77"],
                        "points": 3,
                        "after": "m1",
                        "hint": "Look for a time like 27:00.",
                    },
                ],
            },
        },
    },
    2: {
        "title": "The Vault",
        "roles": {
            "Analyst": {
                "instructions": (
                    "You are inside the attacker's server. Attackers hide things in "
                    "folders whose names start with a dot. Click through the files below "
                    "to explore. Your partner has records you cannot see, so keep "
                    "talking to each other."
                ),
                "evidence": [
                    {"text": "SYSTEM BANNER: 'Storage healthy. No hidden data found on this server.'", "after": None},
                    {"text": "FILES: click a folder to open it, click a file to read it. Hidden folders show up too.", "after": None},
                    {"text": "NOTE: your partner is on the log viewer. They can see login records that you cannot.", "after": None},
                    {"text": "VAULT OPENED. FRAGMENT 2: KS-19C4 (write this down!)", "after": "a2"},
                    {"text": "A new folder named vault appeared next to vault.bin. Open it. The note inside is encrypted.", "after": "a2"},
                    {"text": "CIPHER: this is a Caesar cipher. Every letter was moved forward in the alphabet by a secret number. Your partner can find that number.", "after": "a2"},
                    {"text": "NOTE DECODED. Remember the task name and when it runs. It may matter later.", "after": "a3"},
                ],
                "questions": [
                    {
                        "id": "a1",
                        "prompt": "Find the attacker's hidden folder inside /home. The small .tmp file in it warns you not to trust one thing. What is it? (one word)",
                        "answers": ["banner", "the banner"],
                        "points": 1,
                        "after": None,
                        "hint": "Click home, then the folder whose name starts with a dot, then readme.tmp.",
                    },
                    {
                        "id": "a2",
                        "prompt": "Open the vault. Enter the answer to the security question written in vault.bin.",
                        "answers": ["svc_backup01"],
                        "points": 3,
                        "after": "a1",
                        "hint": "Read vault.bin to see the question. The answer is in your partner's login records. Ask them to look up the 03:07 logins.",
                    },
                    {
                        "id": "a3",
                        "prompt": "Decode the vault note. Which scheduled task does it name? (the second word of the decoded message)",
                        "answers": ["archiveindex", "archive index", "archive_index"],
                        "points": 3,
                        "after": "a2",
                        "hint": "Move every letter BACK by the shift number your partner finds. Example with shift 3: D becomes A, E becomes B. Decode the second word.",
                    },
                ],
            },
            "Monitor": {
                "instructions": (
                    "You are on the NovaCorp log viewer. Your partner is inside the attacker's "
                    "server and will find a locked vault with a security question. Ask them "
                    "what it says, then search the records."
                ),
                "evidence": [
                    {"text": "SYSTEM BANNER: 'All logins verified. No unknown sources detected.'", "after": None},
                    {"text": "FILES: click a folder or file to open it. Read the records carefully. Times are on a 24-hour clock.", "after": None},
                    {"text": "NOTE: company networks are listed in /config/known_networks.txt. Any address not on that list is unknown.", "after": None},
                    {"text": "ACCOUNT AUDIT UNLOCKED: open the audit folder.", "after": "m1"},
                    {"text": "SCRATCHPAD UNLOCKED: the attacker left a file in the config folder. Your partner's vault note may need it.", "after": "m1"},
                ],
                "questions": [
                    {
                        "id": "m1",
                        "prompt": "Your partner is at a locked vault with a security question. Ask them what it says, find the answer in the login records, and enter it here too.",
                        "answers": ["svc_backup01"],
                        "points": 3,
                        "after": None,
                        "hint": "Open logs, then logins.txt, and read the rows for the time in the question (24-hour clock, so 03:07 is early morning). Several users are close, so check each IP in /config/known_networks.txt.",                    },
                    {
                        "id": "m2",
                        "prompt": "When was that account created? Enter the date as DDMM.",
                        "answers": ["0210"],
                        "points": 2,
                        "after": "m1",
                        "hint": "Open audit, then accounts.txt. Day first, then month: 2 October is 0210.",
                    },
                    {
                        "id": "m3",
                        "prompt": "Open the attacker's scratchpad. What cipher shift number does it mention? Tell your partner.",
                        "answers": ["3", "three"],
                        "points": 3,
                        "after": "m1",
                        "hint": "Open the config folder, then scratchpad.txt.",
                    },
                ],
            },
        },
    },
    3: STAGE3_MISSION,
    # ---- Stages 4-5: old one-question format, converted below. ----
    # Rewrite these into the new format one at a time.
    4: STAGE4_MISSION,
    5: {
        "title": "Close the Investigation",
        "roles": {
            "Analyst": {
                "instructions": "Summarize the fictional investigation by naming the insider account.",
                "evidence": [
                    "Review finding: Hydra was quarantined before execution and was a decoy.",
                    "Review finding: jordan.lee created the after-hours ArchiveIndex task.",
                ],
                "question": "Who is the insider threat?",
                "answer_key": "jordan.lee",
            },
            "Monitor": {
                "instructions": "Summarize the fictional investigation by naming the insider account.",
                "evidence": [
                    "Review finding: the suspicious Hydra message led to no external connection.",
                    "Review finding: simulated notices repeatedly traced to jordan.lee.",
                ],
                "question": "Who is the insider threat?",
                "answer_key": "jordan.lee",
            },
        },
    },
}

# Convert the old one-question stages (4-5) into the new multi-question format.
_LEGACY_POINTS = {5: (20, 20)}
for _stage, (_pa, _pm) in _LEGACY_POINTS.items():
    for _role, _pts in (("Analyst", _pa), ("Monitor", _pm)):
        _r = MISSIONS[_stage]["roles"][_role]
        if "questions" not in _r:
            _r["evidence"] = [{"text": t, "after": None} for t in _r["evidence"]]
            _r["questions"] = [
                {
                    "id": "q1",
                    "prompt": _r.pop("question"),
                    "answers": [_r.pop("answer_key").casefold()],
                    "points": _pts,
                    "after": None,
                    "hint": "Re-read the evidence carefully.",
                }
            ]

# Image attachments (like QR codes). Files live in backend/app/assets and are
# only served to the right player after the right question is solved.
ASSETS = {4: STAGE4_ASSETS}

def find_question(stage: int, role: str, qid: str) -> dict | None:
    for q in MISSIONS[stage]["roles"][role]["questions"]:
        if q["id"] == qid:
            return q
    return None


def is_unlocked(stage: int, role: str, q: dict, answered: dict) -> bool:
    return q["after"] is None or answered.get(f"{stage}:{role}:{q['after']}", False)


def check_answer(q: dict, submitted: str) -> bool:
    return submitted.strip().casefold() in q["answers"]

def _asset_open(stage: int, role: str, asset: dict, answered: dict, flags: list) -> bool:
    after = asset.get("after")
    if after is not None and not answered.get(f"{stage}:{role}:{after}", False):
        return False
    need = asset.get("flag")
    if need and f"{stage}:{need}" not in flags:
        return False
    for name in asset.get("flags_all") or []:
        if f"{stage}:{name}" not in flags:
            return False
    return True


def visible_assets(stage: int, role: str, answered: dict, flags: list | None = None) -> list[dict]:
    flags = flags or []
    return [
        {"id": a["id"], "caption": a["caption"]}
        for a in ASSETS.get(stage, {}).get(role, [])
        if _asset_open(stage, role, a, answered, flags)
    ]


def find_asset(stage: int, role: str, asset_id: str, answered: dict,
               flags: list | None = None) -> dict | None:
    flags = flags or []
    for a in ASSETS.get(stage, {}).get(role, []):
        if a["id"] == asset_id and _asset_open(stage, role, a, answered, flags):
            return a
    return None


def _visible(item: dict, stage: int, role: str, answered: dict, flags: list) -> bool:
    after = item.get("after")
    if after is not None and not answered.get(f"{stage}:{role}:{after}", False):
        return False
    need = item.get("flag")
    if need and f"{stage}:{need}" not in flags:
        return False
    hide = item.get("unless")
    if hide and f"{stage}:{hide}" in flags:
        return False
    return True


def _public_tables(r: dict, stage: int, role: str, answered: dict, flags: list) -> list[dict]:
    tables = []
    for t in r.get("tables", []):
        if not _visible(t, stage, role, answered, flags):
            continue
        item = {
            "id": t["id"],
            "title": t["title"],
            "columns": t["columns"],
            "rows": [
                {"id": row["id"], "cells": row["cells"]}
                for row in t["rows"]
                if _visible(row, stage, role, answered, flags)
            ],
        }
        if t.get("pick"):
            item["pick"] = t["pick"]
        tables.append(item)
    return tables


def public_mission(stage: int, role: str, answered: dict | None = None,
                   flags: list | None = None) -> dict:
    """Build the player-facing mission. Never includes answers or hints."""
    answered = answered or {}
    flags = flags or []
    m = MISSIONS[stage]
    r = m["roles"][role]
    questions = []
    for q in r["questions"]:
        if not is_unlocked(stage, role, q, answered):
            continue
        item = {
            "id": q["id"],
            "prompt": q["prompt"],
            "points": q["points"],
            "answered": answered.get(f"{stage}:{role}:{q['id']}", False),
        }
        if q.get("choices"):
            item["choices"] = q["choices"]
        if q.get("pick"):
            item["pick"] = True
        if q.get("kind"):
            item["kind"] = q["kind"]
        if q.get("digits"):
            item["digits"] = q["digits"]
        if q.get("cards"):
            item["cards"] = q["cards"]
        questions.append(item)
    return {
        "stage": stage,
        "title": m["title"],
        "role": role,
        "instructions": r["instructions"],
        "evidence": [
            e["text"] for e in r["evidence"] if _visible(e, stage, role, answered, flags)
        ],
        "questions": questions,
        "tables": _public_tables(r, stage, role, answered, flags),
    }