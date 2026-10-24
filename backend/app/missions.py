"""Server-authored mission content and answer keys.

Answers and hints never leave the server except hints, which are released
only through the /hint endpoint. All answers must be lowercase.
"""

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
    3: {
        "title": "The Phish",
        "roles": {
            "Analyst": {
                "instructions": (
                    "You are in the server's /tmp folder. Your partner has the inbox. "
                    "Compare notes before you touch anything."
                ),
                "evidence": [
                    {"text": "TERMINAL: ls -la /tmp", "after": None},
                    {"text": "FILES: .leave_notice.txt  idx_task.cfg  hydra_stub.bin  sess_91ac.tmp  cache_88.tmp", "after": None},
                    {"text": "hydra_stub.bin: placeholder file, zero network functions. Not a real payload.", "after": None},
                    {"text": "idx_task.cfg: name=ArchiveIndex trigger=after_cleanup", "after": None},
                    {"text": "sess_91ac.tmp: (empty)", "after": None},
                    {"text": "cache_88.tmp: cache rebuilt 08:55 ok", "after": None},
                    {"text": ".leave_notice.txt: 'HR: employee EMP-5120 is on approved leave from 13 Oct to 17 Oct 2026. Do not contact.'", "after": None},
                    {"text": "LOG: partner flagged the inbox message. Ask the Monitor for the fragment.", "after": "a2"},
                ],
                "questions": [
                    {
                        "id": "a1",
                        "prompt": "Which file in /tmp mentions an employee who should be on leave?",
                        "answers": [".leave_notice.txt", "leave_notice.txt"],
                        "points": 2,
                        "after": None,
                        "hint": "Look at the file names. One of them is about HR.",
                    },
                    {
                        "id": "a2",
                        "prompt": "Which employee ID is named in that file? (format EMP-1234)",
                        "answers": ["emp-5120", "5120"],
                        "points": 2,
                        "after": "a1",
                        "hint": "Read the contents of the leave notice.",
                    },
                    {
                        "id": "a3",
                        "prompt": "Enter fragment 3. Your partner gets it once they decide what to do with the email.",
                        "answers": ["ks-7b20"],
                        "points": 3,
                        "after": "a2",
                        "hint": "Ask the Monitor what they decided about the email. The fragment starts with KS-.",
                    },
                ],
            },
            "Monitor": {
                "instructions": (
                    "An urgent email just arrived in your inbox. Your partner is in the "
                    "server's /tmp folder. Do not act on it until you have checked it."
                ),
                "evidence": [
                    {"text": "INBOX: 1 new URGENT message", "after": None},
                    {"text": "FROM: it.admin@nov4corp.example   TO: monitor@novacorp.example   SENT: 14 Oct 2026 03:20", "after": None},
                    {"text": "SUBJECT: URGENT - Hydra is in /tmp. Delete everything there NOW", "after": None},
                    {"text": "BODY: 'Hydra is running from /tmp. Delete every file in /tmp immediately before it spreads. Tell no one. - IT Sysadmin'", "after": None},
                    {"text": "STAFF DIRECTORY: the real company domain is novacorp.example", "after": None},
                    {"text": "TIMELINE: Hydra email first opened 09:12. Hydra alert fired 09:14.", "after": None},
                    {"text": "ROSTER: EMP-4471 avery.park, EMP-5120 jordan.lee, EMP-3308 maria.dsouza", "after": None},
                    {"text": "MAIL LOG: jordan.lee (EMP-5120) opened the Hydra email at 09:31 on 14 Oct.", "after": None},
                    {"text": "EMAIL FLAGGED AS PHISHING. FRAGMENT 3: KS-7B20 (tell your partner!)", "after": "m3"},
                ],
                "questions": [
                    {
                        "id": "m1",
                        "prompt": "What fake domain does the email's sender address use?",
                        "answers": ["nov4corp.example"],
                        "points": 2,
                        "after": None,
                        "hint": "Compare the sender's domain with the real one in the staff directory, letter by letter.",
                    },
                    {
                        "id": "m2",
                        "prompt": "The Hydra alert fired at 09:14. At what time was this email sent? (HH:MM)",
                        "answers": ["03:20", "0320"],
                        "points": 3,
                        "after": "m1",
                        "hint": "Check the SENT field. It is hours before the alert.",
                    },
                    {
                        "id": "m3",
                        "prompt": "Should you delete the files in /tmp as the email asks? Type delete or keep.",
                        "answers": ["keep"],
                        "points": 3,
                        "after": "m2",
                        "hint": "The email is fake, so the files in /tmp are evidence. Do not destroy evidence.",
                    },
                ],
            },
        },
    },
    # ---- Stages 4-5: old one-question format, converted below. ----
    # Rewrite these into the new format one at a time.
    4: {
        "title": "The Insider's Trail",
        "roles": {
            "Analyst": {
                "instructions": "Use the fictional task history to identify the account that created the unusual index task.",
                "evidence": [
                    "Training task record: 'ArchiveIndex' created by jordan.lee at 22:11.",
                    "Task record: the item only indexed fictional case metadata; no files were transferred.",
                ],
                "question": "Which account created ArchiveIndex?",
                "answer_key": "jordan.lee",
            },
            "Monitor": {
                "instructions": "Use the simulated message trail to identify the account associated with the repeated notices.",
                "evidence": [
                    "Training mail header: three archive-index notices were requested by jordan.lee.",
                    "The notices were retained inside the fictional NovaCorp training environment.",
                ],
                "question": "Which account is associated with the repeated notices?",
                "answer_key": "jordan.lee",
            },
        },
    },
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
_LEGACY_POINTS = {4: (10, 10), 5: (20, 20)}

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
ASSETS = {}


def find_question(stage: int, role: str, qid: str) -> dict | None:
    for q in MISSIONS[stage]["roles"][role]["questions"]:
        if q["id"] == qid:
            return q
    return None


def is_unlocked(stage: int, role: str, q: dict, answered: dict) -> bool:
    return q["after"] is None or answered.get(f"{stage}:{role}:{q['after']}", False)


def check_answer(q: dict, submitted: str) -> bool:
    return submitted.strip().casefold() in q["answers"]


def _asset_open(stage: int, role: str, asset: dict, answered: dict) -> bool:
    after = asset["after"]
    return after is None or answered.get(f"{stage}:{role}:{after}", False)


def visible_assets(stage: int, role: str, answered: dict) -> list[dict]:
    return [
        {"id": a["id"], "caption": a["caption"]}
        for a in ASSETS.get(stage, {}).get(role, [])
        if _asset_open(stage, role, a, answered)
    ]


def find_asset(stage: int, role: str, asset_id: str, answered: dict) -> dict | None:
    for a in ASSETS.get(stage, {}).get(role, []):
        if a["id"] == asset_id and _asset_open(stage, role, a, answered):
            return a
    return None


def public_mission(stage: int, role: str, answered: dict | None = None) -> dict:
    """Build the player-facing mission. Never includes answers or hints."""
    answered = answered or {}
    m = MISSIONS[stage]
    r = m["roles"][role]
    return {
        "stage": stage,
        "title": m["title"],
        "role": role,
        "instructions": r["instructions"],
        "evidence": [
            e["text"]
            for e in r["evidence"]
            if e["after"] is None or answered.get(f"{stage}:{role}:{e['after']}", False)
        ],
        "questions": [
            {
                "id": q["id"],
                "prompt": q["prompt"],
                "points": q["points"],
                "answered": answered.get(f"{stage}:{role}:{q['id']}", False),
            }
            for q in r["questions"]
            if is_unlocked(stage, role, q, answered)
        ],
    }