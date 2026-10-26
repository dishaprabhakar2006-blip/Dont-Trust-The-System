"""Stage 3: The Curveball.

Mission text and the fake file systems for both players. It lives in its
own file so it is easy to edit. missions.py and terminal.py import from here.
All answers must be lowercase.

Choice flags: when the Monitor picks keep or delete, the server stores the
flag "3:kept" or "3:deleted". Items with "flag" only show after that choice,
items with "unless" are hidden after it.
"""

FRAGMENT_3 = "KS-7B20"


def _f(text, after=None, flag=None, unless=None):
    """A fake file or evidence line with optional unlock rules."""
    return {"text": text, "after": after, "flag": flag, "unless": unless}


# ------------------------------------------------------------------
# Mission text
# ------------------------------------------------------------------

def _e(text, after=None, flag=None, unless=None):
    return {"text": text, "after": after, "flag": flag, "unless": unless}


MISSION = {
    "title": "The Curveball",
    "roles": {
        "Analyst": {
            "instructions": (
                "You are in the server's /tmp folder, where the incident left its "
                "files. Your partner has the inbox. Compare notes before anything "
                "is touched."
            ),
            "evidence": [
                _e("SYSTEM BANNER: 'Temporary files are safe to remove. No action needed.'"),
                _e("FILES: open the tmp folder in the File Explorer. Hidden files start with a dot."),
                _e("NOTE: your partner is on the mail console. An urgent email just arrived there."),
                _e("YOUR PARTNER KEPT THE FILES. They should be able to give you fragment 3.",
                   flag="kept"),
                _e("ALERT: everything in /tmp was just deleted. A backup of /tmp may still exist in "
                   "/var/backups. Only a backup block that passed its checksum can be trusted.",
                   flag="deleted"),
            ],
            "questions": [
                {
                    "id": "a1",
                    "prompt": "Which file in /tmp mentions an employee who should be on leave?",
                    "answers": [".notice.txt", ".notice.txt"],
                    "points": 2,
                    "after": None,
                    "hint": "Open the tmp folder. One file is from HR, and hidden files start with a dot.",
                },
                {
                    "id": "a2",
                    "prompt": "Which employee ID is named in that file? (format EMP-1234)",
                    "answers": ["emp-5120", "5120"],
                    "points": 2,
                    "after": "a1",
                    "hint": "Open the leave notice and read it. The ID looks like EMP-1234.",
                },
                {
                    "id": "a3",
                    "prompt": "Enter fragment 3 (it starts with KS-). Your partner may have it, "
                              "or you may have to recover it yourself.",
                    "answers": ["ks-7b20"],
                    "points": 3,
                    "after": "a2",
                    "hint": "Ask your partner what they decided about the email. If the files were "
                            "deleted, open /var/backups and read restore.log.",
                },
            ],
        },
        "Monitor": {
            "instructions": (
                "An urgent email just arrived in your inbox. Your partner is in the "
                "server's /tmp folder. Do not act on it until you have checked it."
            ),
            "evidence": [
                _e("SYSTEM BANNER: 'Inbox clean. No suspicious messages.'"),
                _e("NEW MAIL: 1 URGENT message. Open the mail folder, then inbox, to read it."),
                _e("NOTE: the real company email domain is in config/staff_directory.txt. "
                   "Delivery times are in the logs folder."),
                _e("EMAIL FLAGGED AS PHISHING. FRAGMENT 3: KS-7B20 (make note of it and tell your partner!)",
                   flag="kept"),
                _e("EVIDENCE DESTROYED: -3 points. The fragment was inside those files. Your "
                   "partner may still recover it from the backup in /var/backups. Help them.",
                   flag="deleted"),
            ],
            "questions": [
                {
                    "id": "m1",
                    "prompt": "What fake domain does the email's sender address use?",
                    "answers": ["nov4corp.example"],
                    "points": 2,
                    "after": None,
                    "hint": "Compare the sender's domain with the real one in config/staff_directory.txt, "
                            "letter by letter.",
                },
                {
                    "id": "m2",
                    "prompt": "The Hydra alert fired at 09:14. At what time was this email sent? (HH:MM)",
                    "answers": ["03:20", "0320"],
                    "points": 3,
                    "after": "m1",
                    "hint": "Read the Date line of the email, then check logs/alerts.txt for the alert time.",
                },
                {
                    "id": "m3",
                    "prompt": "Decide what to do with the files in /tmp.",
                    "answers": ["keep", "delete"],
                    "points": 3,
                    "after": "m2",
                    "choices": [
                        {"label": "Keep the files in /tmp", "value": "keep",
                         "confirm": "Keep the files in /tmp?"},
                        {"label": "Delete everything in /tmp", "value": "delete",
                         "confirm": "Delete everything in /tmp?"},
                    ],
                    "effects": {
                        "keep": {"flag": "kept"},
                        "delete": {"flag": "deleted", "points": 0, "penalty": 3},
                    },
                    "hint": "The email is fake, so the files in /tmp are evidence. Do not destroy evidence.",
                },
            ],
        },
    },
}


# ------------------------------------------------------------------
# Fake file systems
# ------------------------------------------------------------------

_TMP_FILES = {
    "/tmp/.notice.txt": (
        "HR NOTICE\n"
        "Employee EMP-5120 is on approved leave from 13 Oct to 17 Oct 2026.\n"
        "Do not contact. Access is suspended during leave."
    ),
    "/tmp/idx_task.cfg": (
        "name=ArchiveIndex\n"
        "trigger=after_cleanup\n"
        "owner=svc_backup01\n"
        "status=waiting"
    ),
    "/tmp/hydra_stub.bin": (
        "[placeholder file]\n"
        "scan result: zero network functions found.\n"
        "this file cannot connect to anything."
    ),
    "/tmp/sess_91ac.tmp": "(empty)",
    "/tmp/sess_4d2e.tmp": "(empty)",
    "/tmp/cache_88.tmp": "cache rebuilt 08:55 ok",
    "/tmp/build_4419.log": "build 4419 ok\nbuild 4420 ok\nbuild 4421 ok",
    "/tmp/pip-install.txt": "installed 14 packages. no errors.",
    "/tmp/.font_cache": "font cache. nothing useful here.",
}

_BAD_BLOCKS = {
    7: "block 07 checksum FAILED note=KS-7B02",
    12: "block 12 checksum FAILED note=KS-7D20",
    17: "block 17 checksum ok note=" + FRAGMENT_3,
    21: "block 21 checksum FAILED note=KS-B720",
}

_RESTORE_LOG = "\n".join(
    [
        "BACKUP RESTORE LOG (snapshot of /tmp, 14 Oct 09:30)",
        "A block that FAILED its checksum is corrupted. Do not trust it.",
        "",
    ]
    + [_BAD_BLOCKS.get(n, f"block {n:02d} checksum ok") for n in range(1, 25)]
)


def _analyst_files() -> dict:
    files = {
        "/README.txt": _f(
            "NOVA-DB02 admin console\n"
            "Logged in as: admin\n"
            "Temporary files from the incident are in /tmp."
        ),
        "/etc/motd": _f("NovaCorp internal system. Authorised use only."),
        "/var/log/syslog": _f(
            "14 Oct 03:00:01 cron: nightly job ok\n"
            "14 Oct 09:14:02 av: Hydra_Update quarantined\n"
            "14 Oct 09:15:30 cron: 1 job waiting for event 'cleanup'"
        ),
    }
    for path, text in _TMP_FILES.items():
        files[path] = _f(text, unless="deleted")
        files["/var/backups/tmp_snapshot" + path[len("/tmp"):]] = _f(text, flag="deleted")
    files["/tmp/.deleted_by_admin.log"] = _f(
        "rm -rf /tmp/*   (run from the Monitor console)\n"
        "INTEGRITY WARNING: evidence destroyed.",
        flag="deleted",
    )
    files["/var/backups/manifest.txt"] = _f(
        "snapshot of /tmp taken 14 Oct 09:30\n"
        "files: 9\n"
        "see restore.log for the block checks",
        flag="deleted",
    )
    files["/var/backups/restore.log"] = _f(_RESTORE_LOG, flag="deleted")
    files["/var/log/cleanup_event.log"] = _f(
        "14 Oct 09:41:07 cleanup event received (rm -rf /tmp/*)\n"
        "14 Oct 09:41:08 scheduler: ArchiveIndex armed (trigger after_cleanup)",
        flag="deleted",
    )
    return files


def _monitor_files() -> dict:
    return {
        "/README.txt": _f(
            "NOVA-SIEM mail and log console\n"
            "Logged in as: monitor\n"
            "New mail is in /mail/inbox. Logs are in /logs and settings are in /config."
        ),
        "/mail/inbox/URGENT_hydra_in_tmp.eml": _f(
            "From: it.admin@nov4corp.example\n"
            "To: monitor@novacorp.example\n"
            "Date: 14 Oct 2026 03:20\n"
            "X-Originating-IP: 203.0.113.77\n"
            "Subject: URGENT - Hydra is in /tmp. Delete everything there NOW\n"
            "\n"
            "Hydra is running from /tmp. Delete every file in /tmp immediately\n"
            "before it spreads. Tell no one.\n"
            "\n"
            "- IT Sysadmin"
        ),
        "/mail/inbox/lunch_friday.eml": _f(
            "From: priya.nair@novacorp.example\n"
            "To: all-staff@novacorp.example\n"
            "Date: 13 Oct 2026 16:40\n"
            "Subject: Team lunch Friday\n"
            "\n"
            "Lunch is at 1pm in room 4B. Reply if you have dietary needs."
        ),
        "/mail/inbox/rota_update.eml": _f(
            "From: ben.carter@novacorp.example\n"
            "To: all-staff@novacorp.example\n"
            "Date: 13 Oct 2026 11:05\n"
            "Subject: Rota updated\n"
            "\n"
            "Next week's rota is on the shared drive. Swap requests by Thursday."
        ),
        "/mail/inbox/hr_leave_reminder.eml": _f(
            "From: hr@novacorp.example\n"
            "To: all-staff@novacorp.example\n"
            "Date: 14 Oct 2026 08:02\n"
            "Subject: Leave reminder\n"
            "\n"
            "Three staff are on approved leave this week. Their accounts are restricted\n"
            "until they return. Contact HR with questions."
        ),
        "/mail/inbox/q3_numbers.eml": _f(
            "From: avery.park@novacorp.example\n"
            "To: finance@novacorp.example\n"
            "Date: 13 Oct 2026 17:20\n"
            "Subject: Q3 numbers\n"
            "\n"
            "Final Q3 numbers are in the finance folder. No changes since Monday."
        ),
        "/config/staff_directory.txt": _f(
            "NOVACORP STAFF DIRECTORY\n"
            "Company email domain: novacorp.example\n"
            "IT contact: it.helpdesk@novacorp.example\n"
            "\n"
            "EMP-4471  avery.park     Finance\n"
            "EMP-5120  jordan.lee     IT Support\n"
            "EMP-3308  maria.dsouza   Operations\n"
            "EMP-2290  priya.nair     Admin\n"
            "EMP-3871  ben.carter     HR"
        ),
        "/logs/mail.log": _f(
            "14 Oct 02:14:08 delivered priya.nair@novacorp.example -> ben.carter@novacorp.example subject='rota swap'\n"
            "14 Oct 03:20:11 delivered it.admin@nov4corp.example -> monitor@novacorp.example "
            "subject='URGENT - Hydra is in /tmp. Delete everything there NOW' relay=203.0.113.77\n"
            "14 Oct 08:02:40 delivered hr@novacorp.example -> all-staff@novacorp.example subject='Leave reminder'\n"
            "14 Oct 09:05:51 delivered security-update@novacorp-updates.invalid -> avery.park@novacorp.example "
            "subject='Urgent security update'\n"
            "14 Oct 10:30:22 delivered avery.park@novacorp.example -> finance@novacorp.example subject='Q3 numbers'"
        ),
        "/logs/alerts.txt": _f(
            "14 Oct 09:14:02 ALERT Hydra_Update quarantined (nova-ws12), no outbound connection\n"
            "14 Oct 09:14:03 FIREWALL BLOCK nova-ws12 -> 198.51.100.24\n"
            "14 Oct 11:30:00 INFO nightly report generated"
        ),
    }


TERMINAL = {
    "Analyst": {"host": "nova-db02", "files": _analyst_files()},
    "Monitor": {"host": "nova-siem", "files": _monitor_files()},
}