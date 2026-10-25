"""Stage 5: The Crisis.

After the fake SYSTEM SECURED screen the attacker reveals that Hydra was a
decoy. An upload is running. Both players act at once:

  Monitor  blocks the steady stream (row n8443) among 40 connections.
  Analyst  disables the hidden account and the "after cleanup" task.
  Both     name the insider. Right name = full points, wrong name = half.

The countdown runs on the server (see main.py). All answers are lowercase.
Flags: ip_blocked, account_disabled, task_disabled, insider_right, insider_wrong.
"""

import random


def _e(text):
    return {"text": text, "after": None, "flag": None, "unless": None}


def _row(rid, cells, unless=None):
    return {"id": rid, "cells": cells, "unless": unless}


def _table(tid, title, columns, rows, pick=None):
    t = {"id": tid, "title": title, "columns": columns, "rows": rows}
    if pick:
        t["pick"] = pick
    return t


SUSPECTS = ["avery.park", "jordan.lee", "maria.dsouza", "ben.carter",
            "priya.nair", "contractor.ray"]


def _insider(prompt, points, qid):
    return {
        "id": qid,
        "prompt": prompt,
        "points": points,
        "after": None,
        "answers": SUSPECTS,
        "choices": [{"label": s, "value": s, "confirm": f"Name {s} as the insider?"}
                    for s in SUSPECTS],
        "effects": {
            s: ({"flag": "insider_right"} if s == "jordan.lee"
                else {"flag": "insider_wrong", "points": points // 2})
            for s in SUSPECTS
        },
        "hint": "Put your tables together. Who was on leave but still logged in, and "
                "opened the fake email? Your partner has the other half of that fact.",
    }


# ---------------- Analyst data ----------------
_ACCOUNTS = [
    ("avery.park", "employee", "2021-03-08", "HR-0112", "08:41"),
    ("jordan.lee", "employee", "2019-06-17", "HR-0044", "13:07"),
    ("maria.dsouza", "employee", "2020-01-13", "HR-0087", "02:30"),
    ("ben.carter", "employee", "2022-09-05", "HR-0203", "11:12"),
    ("priya.nair", "employee", "2023-02-20", "HR-0251", "14:20"),
    ("contractor.ray", "contractor", "2026-09-14", "HR-0388", "03:07"),
    ("svc_backup", "service", "2020-05-02", "REQ-0090", "03:00"),
    ("svc_sql", "service", "2020-05-02", "REQ-0188", "06:02"),
    ("svc_web", "service", "2021-08-19", "REQ-0201", "06:03"),
    ("svc_it", "service", "2022-04-11", "REQ-0267", "09:14"),
    ("svc_monitor", "service", "2022-11-30", "REQ-0412", "06:10"),
    ("svc_backup01", "service", "2026-10-02", "none", "03:07"),
    ("svc_report", "service", "2023-07-03", "REQ-0333", "05:00"),
    ("svc_print", "service", "2021-01-25", "REQ-0150", "09:20"),
    ("guest_lab", "guest", "2024-06-10", "HR-0301", "never"),
    ("admin", "admin", "2018-01-01", "REQ-0001", "10:02"),
]
_TASKS = [
    ("t1", "NightlyBackup", "svc_backup", "daily 03:00", "ok"),
    ("t2", "LogRotate", "svc_it", "daily 04:30", "ok"),
    ("t3", "UpdateCheck", "SYSTEM", "daily 05:00", "ok"),
    ("t4", "CleanupTemp", "svc_it", "daily 06:00", "ok"),
    ("archiveindex", "ArchiveIndex", "svc_backup01", "after_cleanup", "waiting"),
    ("t6", "ArchiveIndexer", "svc_sql", "weekly Sun 01:00", "ok"),
    ("t7", "AVScan", "SYSTEM", "daily 02:00", "ok"),
    ("t8", "ReportBuild", "svc_report", "daily 05:30", "ok"),
    ("t9", "PrintQueueClean", "svc_print", "every 4 hours", "ok"),
    ("t10", "DBVacuum", "svc_sql", "weekly Sat 23:00", "ok"),
    ("t11", "CertRenew", "SYSTEM", "monthly 1st", "ok"),
    ("t12", "HealthPing", "svc_monitor", "every 5 min", "ok"),
    ("t13", "IndexRebuild", "svc_sql", "daily 01:30", "ok"),
    ("t14", "TempScan", "svc_it", "after_scan", "ok"),
]
_LEAVE = [
    ("avery.park", "EMP-4471", "Finance", "none"),
    ("jordan.lee", "EMP-5120", "IT Support", "13 to 17 Oct"),
    ("maria.dsouza", "EMP-3308", "Operations", "none"),
    ("ben.carter", "EMP-3871", "HR","12 to 16 Oct"),
    ("priya.nair", "EMP-2290", "Admin", "14 to 15 Oct"),
    ("contractor.ray", "EXT-0042", "Contractor", "n/a"),
]

# ---------------- Monitor data ----------------
_LOGINS = [
    ("02:30", "maria.dsouza", "10.0.4.50", "approved maintenance"),
    ("03:07:30", "contractor.ray", "vpn pool 10.0.9.x", "known VPN"),
    ("03:07:41", "svc_backup01", "203.0.113.77", "session opened"),
    ("08:41", "avery.park", "10.0.4.21", "login ok"),
    ("09:12", "avery.park", "10.0.4.21", "opened Hydra email"),
    ("09:31", "jordan.lee", "10.0.4.35", "opened Hydra email"),
    ("11:12", "maria.dsouza", "10.0.4.50", "login ok"),
    ("13:07", "jordan.lee", "10.0.4.35", "login ok"),
    ("14:20", "avery.park", "10.0.4.21", "login ok"),
]
_SPIKY = ["▁▁▁█▁▁▁█▁▁▁█", "▂▅▁▇▃▂▆▁▄▂▁▅", "▁▇▁▁▆▁▁▇▁▁▅▁", "▃▂▄▃▅▂▃▄▂▃▂▄", "▂▃▂▅▃▂▄▃▂▃▅▃"]
_FLAT = "▃▃▃▃▃▃▃▃▃▃▃▃"


def _connections():
    r = random.Random(505)
    used = {8443}
    rows = []

    def port():
        p = r.randrange(1100, 9900)
        while p in used:
            p = r.randrange(1100, 9900)
        used.add(p)
        return p

    def ext():
        return "%d.%d.%d.%d" % (r.choice([104, 142, 151, 93, 172]),
                                r.randrange(1, 250), r.randrange(1, 250), r.randrange(1, 250))

    def internal():
        return "10.0.4.%d" % r.randrange(5, 99)

    def add(remote, sent, pattern):
        p = port()
        since = "%02d:%02d" % (r.randrange(6, 14), r.randrange(60))
        rows.append(_row(f"n{p}", [str(p), remote, sent, since, pattern]))

    for i in range(34):
        add(internal() if i % 3 == 0 else ext(),
            "%d %s" % (r.randrange(2, 900), r.choice(["KB", "KB", "MB"])), r.choice(_SPIKY))
    for _ in range(3):
        add(ext(), "%d KB" % r.randrange(8, 40), _FLAT)          # tiny keepalives
    for _ in range(3):
        add(internal(), "%d KB" % r.randrange(100, 300), _FLAT)  # internal, flat
    r.shuffle(rows)
    rows.insert(19, _row("n8443", ["8443", "203.0.113.77", "61 MB", "03:07", _FLAT],
                         unless="ip_blocked"))
    return rows


MISSION = {
    "title": "The Crisis",
    "roles": {
        "Analyst": {
            "instructions": (
                "Hydra was a decoy. A hidden insider is copying NovaCorp's data out right "
                "now. You see the accounts and scheduled tasks. Disable the hidden account "
                "and its task, then name the insider with your partner. Check your notes."
            ),
            "evidence": [
                _e("ATTACKER: 'Thanks for killing Hydra. You just gave me the time I needed.'"),
                _e("The upload is running. Your partner traces it. You shut down the account "
                   "and the task. Wrong clicks count as wrong answers."),
                _e("Clues from earlier rounds matter. Your notes may save you minutes."),
            ],
            "tables": [
                _table("acc", "Accounts (NOVA-DB02)",
                       ["User", "Type", "Created", "HR request", "Status"],
                       [_row(u, [u, t, c, h, "active"], "account_disabled" if u == "svc_backup01" else None)
                        for u, t, c, h, l in _ACCOUNTS],
                       {"question": "a1", "label": "Disable",
                        "confirm": "Disable this account? A wrong choice counts as a wrong answer."}),
                _table("task", "Scheduled tasks",
                       ["Task", "Owner", "Trigger", "Status"],
                       [_row(i, [n, o, t, s], "task_disabled" if i == "archiveindex" else None)
                        for i, n, o, t, s in _TASKS],
                       {"question": "a2", "label": "Disable",
                        "confirm": "Disable this task? A wrong choice counts as a wrong answer."}),
                _table("leave", "HR leave records",
                       ["Name", "ID", "Department", "Leave"],
                       [_row(f"l{i}", list(x)) for i, x in enumerate(_LEAVE)]),
            ],
            "questions": [
                {"id": "a1", "points": 7, "after": None, "answers": ["svc_backup01"],
                 "prompt": "Disable the hidden account. It should not exist.",
                 "pick": True, "effects": {"svc_backup01": {"flag": "account_disabled"}},
                 "hint": "Real service accounts have an HR request number. One account has none "
                         "and was created in October."},
                {"id": "a2", "points": 7, "after": None, "answers": ["archiveindex"],
                 "prompt": "Disable the task that runs after cleanup and belongs to that account.",
                 "pick": True, "effects": {"archiveindex": {"flag": "task_disabled"}},
                 "hint": "Check the Owner and Trigger columns. Beware of names that look alike."},
                _insider("Name the insider. RULE: the insider is the employee who was on approved leave on 14 Oct (the incident date) but still logged in that day. Right name earns 6 points, a wrong name earns 3.", 6, "a3"),            ],
        },
        "Monitor": {
            "instructions": (
                "Hydra was a decoy. Data is leaving NovaCorp right now. You see every "
                "connection and the login records. Block the steady stream, then name the "
                "insider with your partner. Check your notes."
            ),
            "evidence": [
                _e("ATTACKER: 'Thanks for killing Hydra. You just gave me the time I needed.'"),
                _e("Find the stream that never stops. Spikes are normal traffic. Block the "
                   "right address and the upload halts."),
                _e("Clues from earlier rounds matter. Your notes may save you minutes."),
            ],
            "tables": [
                _table("net", "Outbound traffic",
                       ["Port", "Remote address", "Sent", "Since", "Last 30 seconds"],
                       _connections(),
                       {"question": "m1", "label": "Block",
                        "confirm": "Block this address? A wrong choice counts as a wrong answer."}),
                _table("log", "Login records, 14 Oct",
                       ["Time", "User", "From", "Note"],
                       [_row(f"g{i}", list(x)) for i, x in enumerate(_LOGINS)]),
            ],
            "questions": [
                {"id": "m1", "points": 10, "after": None, "answers": ["n8443"],
                 "prompt": "Block the steady stream that is stealing the data.",
                 "pick": True, "effects": {"n8443": {"flag": "ip_blocked"}},
                 "hint": "Ignore the spikes. Look for an outside address with a perfectly flat "
                         "line, a large total and a start time in the early morning."},
                _insider("Name the insider. RULE: the insider is the employee who was on approved leave on 14 Oct (the incident date) but still logged in that day. Right name earns 10 points, a wrong name earns 5.", 10, "m2"),            ],
        },
    },
}