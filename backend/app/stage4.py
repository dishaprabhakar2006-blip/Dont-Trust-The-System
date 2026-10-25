"""Stage 4: The Core Dump.

Hydra dies, but its memory dump arrives as a damaged QR code cut into 6 tiles.
Four locks guard the tiles. Each lock is a different kind of puzzle:

  1. TRACE  Monitor reads activity lines to find Hydra's port, Analyst matches
            the port to a process and ends it.            -> tiles 1 and 2
  2. HEX    Analyst has hex bytes, Monitor has the table.  -> tile 3
  3. DIAL   Each player counts rows for the OTHER player's dial. Both dials
            must be set right.                              -> tiles 4 and 5
  4. ORDER  Five events must be put in time order. The Monitor knows two of
            the times, the Analyst knows three.             -> tile 6

Then the players rebuild the QR on the Core Dump board, scan it with a phone,
and join the four fragments into the kill-switch.

Flags set by correct answers: hydra_killed, hex_open, dial_a, dial_m, order_open.
All answers must be lowercase.
"""

FRAGMENT_4 = "KS-4D91"
QR_TEXT = FRAGMENT_4


def _e(text, after=None, flag=None, unless=None):
    return {"text": text, "after": after, "flag": flag, "unless": unless}


def _p(pid, name, user, started, port="-", unless=None):
    """One row of the Analyst's process table. The row id is p<PID>."""
    return {"id": f"p{pid}", "cells": [str(pid), name, user, started, str(port)],
            "unless": unless}


def _n(port, remote, sent, pattern, status, unless=None):
    """One row of the Monitor's network table. The row id is n<port>."""
    return {"id": f"n{port}", "cells": [str(port), remote, sent, pattern, status],
            "unless": unless}


KILL_SWITCH_ANSWERS = ["ks-a7f3-19c4-7b20-4d91", "a7f3-19c4-7b20-4d91"]

KILL_SWITCH_PROMPT = (
    "Build the kill-switch. Join fragments 1 to 4 in order, with dashes, and write "
    "KS- only once at the start. Format: KS-XXXX-XXXX-XXXX-XXXX"
)

DIAL_RIDDLE_INTRO = (
    "DIAL RIDDLES for your PARTNER's dial. Count only the rows still listed in YOUR "
    "table, then tell your partner the three digits in order:"
)

MISSION = {
    "title": "The Core Dump",
    "roles": {
        # ------------------------------------------------------------------
        "Analyst": {
            "instructions": (
                "You are on the server's process manager. Hydra is running under a "
                "disguised name. You can see which process owns which port, but not "
                "who it talks to. Your partner sees the network side. Match the port. "
                "After Hydra dies, its memory dump arrives as a damaged QR code, and "
                "locks guard the pieces."
            ),
            "evidence": [
                _e("SYSTEM BANNER: 'All processes verified safe.'"),
                _e("NOTE: your partner sees ports and remote addresses but not process names. "
                   "You see process names but not remote addresses. The PORT number connects "
                   "your two screens."),
                _e("WARNING: ending the wrong process counts as a wrong answer. Be sure before "
                   "you click."),
                _e("PROCESS TERMINATED. Hydra's core dump arrived as a damaged QR code cut into "
                   "6 tiles. Your Core Dump board is under the table. Three more locks guard "
                   "the tiles.", flag="hydra_killed"),
                _e("HEX LOCK: the dump header is one word written in hex. Each pair of digits "
                   "is one letter.", flag="hydra_killed"),
                _e("CORE DUMP HEADER (hex): 53 48 41 44 4F 57", flag="hydra_killed"),
                _e("Your partner has the hex table. You have the header.", flag="hydra_killed"),
                _e(DIAL_RIDDLE_INTRO, flag="hydra_killed"),
                _e("1) How many processes started at 09:14?", flag="hydra_killed"),
                _e("2) How many processes belong to a user whose name starts with svc_ ?",
                   flag="hydra_killed"),
                _e("3) How many processes belong to avery.park?", flag="hydra_killed"),
                _e("ORDER LOCK: you know three of the five times. The hidden account opened "
                   "its session at 03:07. The fake email was sent at 03:20. The employee who "
                   "was on leave logged in at 13:07.", flag="hydra_killed"),
            ],
            "tables": [
                {
                    "id": "proc",
                    "title": "Process Manager (NOVA-DB02)",
                    "columns": ["PID", "Name", "User", "Started", "Port"],
                    "pick": {
                        "question": "a2",
                        "label": "End process",
                        "confirm": "End this process? Ending the wrong one counts as a wrong answer.",
                    },
                    "rows": [
                        _p(4, "System", "SYSTEM", "06:00"),
                        _p(412, "smss.exe", "SYSTEM", "06:00"),
                        _p(688, "services.exe", "SYSTEM", "06:00"),
                        _p(704, "lsass.exe", "SYSTEM", "06:00"),
                        _p(812, "svchost.exe", "SYSTEM", "06:00", 135),
                        _p(836, "svchost.exe", "NETWORK SERVICE", "06:00", 6000),
                        _p(1188, "sysmon_helper.exe", "svc_backup01", "03:07", 8443),
                        _p(1204, "sqlservr.exe", "svc_sql", "06:02", 1433),
                        _p(1290, "nova-intranet.exe", "svc_web", "06:03", 8080),
                        _p(1344, "filesrv.exe", "SYSTEM", "06:03", 445),
                        _p(1402, "backup-agent.exe", "svc_backup", "06:05", 22),
                        _p(1560, "printspool.exe", "SYSTEM", "06:05", 9100),
                        _p(1722, "rdpsvc.exe", "SYSTEM", "06:06", 3389),
                        _p(2048, "explorer.exe", "avery.park", "08:41"),
                        _p(2210, "chrome.exe", "avery.park", "08:55", 443),
                        _p(2466, "Hydra_Update.exe (quarantined)", "avery.park", "09:14"),
                        _p(2900, "notepad.exe", "ben.carter", "09:48"),
                        _p(3188, "svc_updater.exe", "SYSTEM", "09:14", 5050, unless="hydra_killed"),
                        _p(3240, "patch_installer.exe", "svc_it", "09:14", 5051),
                        _p(3302, "wuauclt.exe", "SYSTEM", "09:25"),
                        _p(3560, "taskhostw.exe", "SYSTEM", "06:07"),
                        _p(3622, "cmd.exe", "admin", "10:02"),
                        _p(3710, "av_service.exe", "SYSTEM", "06:01"),
                    ],
                },
            ],
            "questions": [
                {
                    "id": "a1",
                    "prompt": "Your partner can see which connection phones home on a fixed timer. "
                              "Ask them for its port, find the process that owns that port, and "
                              "enter its PID.",
                    "answers": ["3188"],
                    "points": 1,
                    "after": None,
                    "hint": "Two processes started at 09:14, so the start time cannot decide. "
                            "Ask your partner for the port number and look in the Port column.",
                },
                {
                    "id": "a2",
                    "prompt": "End the Hydra process. Use the End process button on its row in the table.",
                    "answers": ["p3188"],
                    "points": 3,
                    "after": "a1",
                    "pick": True,
                    "effects": {"p3188": {"flag": "hydra_killed"}},
                    "hint": "Click End process on the row whose PID you just entered.",
                },
                {
                    "id": "a3",
                    "prompt": "HEX LOCK: decode the header. What word does it spell?",
                    "answers": ["shadow"],
                    "points": 2,
                    "after": "a2",
                    "effects": {"shadow": {"flag": "hex_open"}},
                    "hint": "Ask your partner for the hex table. Each pair of digits is one letter, "
                            "for example 41 is A and 53 is S.",
                },
                {
                    "id": "a4",
                    "prompt": "DIAL LOCK: set your dial. Your partner's screen has three riddles about "
                              "THEIR table. Their three counts, in order, are your three digits.",
                    "kind": "dial",
                    "digits": 3,
                    "answers": ["5-4-8"],
                    "points": 2,
                    "after": "a3",
                    "effects": {"5-4-8": {"flag": "dial_a"}},
                    "hint": "Ask your partner to read you their three riddles and count the rows in "
                            "their network table. Remember: only the rows still listed.",
                },
                {
                    "id": "a5",
                    "prompt": KILL_SWITCH_PROMPT,
                    "answers": KILL_SWITCH_ANSWERS,
                    "points": 2,
                    "after": "a4",
                    "hint": "You need all four fragments from your notes, in order 1, 2, 3, 4. "
                            "Fragment 4 comes from the QR code.",
                },
            ],
        },
        # ------------------------------------------------------------------
        "Monitor": {
            "instructions": (
                "You are on the network monitor. You can see every connection, its port and "
                "where it sends data, but not which process owns it. Your partner sees the "
                "process names. Find Hydra's connection and give them the port. After Hydra "
                "dies, its memory dump arrives as a damaged QR code, and locks guard the pieces."
            ),
            "evidence": [
                _e("SYSTEM BANNER: 'Network normal. All connections approved.'"),
                _e("THREAT INTEL: Hydra checks in with its server on a fixed timer. Look for an "
                   "EXTERNAL address (not 10.0.4.x) whose line shows sharp spikes at regular "
                   "intervals. Small internal heartbeats are normal, a noisy line is ordinary "
                   "traffic, and a perfectly flat line is a steady stream, not a timer."),
                _e("NOTE: you see ports and addresses but not process names. Your partner sees "
                   "process names but not addresses. The PORT number connects your two screens."),
                _e("HYDRA TERMINATED. Its core dump arrived as a damaged QR code cut into 6 "
                   "tiles. Your Core Dump board is under the table. Three more locks guard "
                   "the tiles.", flag="hydra_killed"),
                _e("NOTE: the Hydra line is gone, but one connection is still sending a "
                   "perfectly steady stream and did not stop. Write it down.",
                   flag="hydra_killed"),
                _e("HEX LOCK: your partner has the header. You have the table. HEX TABLE "
                   "(code = letter):", flag="hydra_killed"),
                _e("41=A 42=B 43=C 44=D 45=E 46=F 47=G", flag="hydra_killed"),
                _e("48=H 49=I 4A=J 4B=K 4C=L 4D=M 4E=N", flag="hydra_killed"),
                _e("4F=O 50=P 51=Q 52=R 53=S 54=T 55=U", flag="hydra_killed"),
                _e("56=V 57=W 58=X 59=Y 5A=Z", flag="hydra_killed"),
                _e(DIAL_RIDDLE_INTRO, flag="hydra_killed"),
                _e("1) How many connections go to internal addresses (10.0.4.x)?", flag="hydra_killed"),
                _e("2) How many connections go to external addresses?", flag="hydra_killed"),
                _e("3) How many connections are ESTABLISHED?", flag="hydra_killed"),
                _e("ORDER LOCK: you know two of the five times. The approved maintenance login "
                   "was at 02:30. Hydra_Update was quarantined at 09:14.", flag="hydra_killed"),
            ],
            "tables": [
                {
                    "id": "net",
                    "title": "Network Monitor (NOVA-DB02)",
                    "columns": ["Local port", "Remote address", "Sent", "Last 30 seconds", "Status"],
                    "rows": [
                        _n(22, "10.0.4.9", "6 MB", "▁▃▁▃▁▃▁▃▁▃▁▃", "ESTABLISHED"),
                        _n(445, "10.0.4.35", "212 MB", "▂▃▂▅▃▂▄▃▂▃▅▃", "ESTABLISHED"),
                        _n(1433, "10.0.4.62", "48 MB", "▃▄▃▃▅▃▄▃▃▄▃▃", "ESTABLISHED"),
                        _n(3389, "10.0.4.50", "2 MB", "▁▁▂▁▁▃▁▁▂▁▁▁", "ESTABLISHED"),
                        _n(5050, "198.51.100.24", "18 MB", "▁▁▁█▁▁▁█▁▁▁█", "ESTABLISHED",
                           unless="hydra_killed"),
                        _n(5051, "198.51.100.25", "3 KB", "▂▅▁▇▃▂▆▁▄▂▁▅", "TIME_WAIT"),
                        _n(6000, "142.250.80.46", "2 MB", "▃▂▄▃▅▂▃▄▂▃▂▄", "ESTABLISHED"),
                        _n(8080, "93.184.216.34", "1 MB", "▂▂▃▂▂▄▂▂▃▂▂▂", "ESTABLISHED"),
                        _n(8443, "203.0.113.77", "38 MB", "▃▃▃▃▃▃▃▃▃▃▃▃", "ESTABLISHED"),
                        _n(9100, "10.0.4.88", "180 KB", "▁▁▁▁▁▁▁▁▁▁▁▁", "ESTABLISHED"),
                    ],
                },
            ],
            "questions": [
                {
                    "id": "m1",
                    "prompt": "TRACE LOCK: which local port phones home to an external address on a "
                              "fixed timer (sharp spikes at regular intervals)? Tell your partner.",
                    "answers": ["5050"],
                    "points": 2,
                    "after": None,
                    "hint": "Ignore the Sent column. Look at the Last 30 seconds lines: you want an "
                            "external address with sharp spikes at regular intervals.",
                },
                {
                    "id": "m2",
                    "prompt": "DIAL LOCK: set your dial. Your partner's screen has three riddles about "
                              "THEIR table. Their three counts, in order, are your three digits.",
                    "kind": "dial",
                    "digits": 3,
                    "answers": ["2-5-3"],
                    "points": 2,
                    "after": "m1",
                    "effects": {"2-5-3": {"flag": "dial_m"}},
                    "hint": "Wait until Hydra is ended. Then ask your partner to read you their three "
                            "riddles and count the rows in their process table.",
                },
                {
                    "id": "m3",
                    "prompt": "ORDER LOCK: put these five events in the order they happened. You know "
                              "two of the times and your partner knows three. Click the events in order.",
                    "kind": "order",
                    "cards": [
                        {"id": "d", "text": "Hydra_Update was quarantined"},
                        {"id": "a", "text": "The hidden account opened a session from outside"},
                        {"id": "e", "text": "The employee on leave logged in anyway"},
                        {"id": "c", "text": "The approved maintenance login"},
                        {"id": "b", "text": "The fake sysadmin email was sent"},
                    ],
                    "answers": ["c,a,b,d,e"],
                    "points": 2,
                    "after": "m2",
                    "effects": {"c,a,b,d,e": {"flag": "order_open"}},
                    "hint": "Ask your partner for their three times. Earliest first: 02:30, 03:07, "
                            "03:20, 09:14, 13:07.",
                },
                {
                    "id": "m4",
                    "prompt": "QR PUZZLE: when all four locks are open, rebuild the QR code on the Core "
                              "Dump board (click a tile, then click another to swap, or press Rotate), "
                              "scan it with your phone and enter fragment 4.",
                    "answers": ["ks-4d91", "4d91"],
                    "points": 2,
                    "after": "m3",
                    "hint": "The three big squares go in three corners, and the outer edge of the code "
                            "has a white border. If your camera cannot scan it, the text is KS-4D91.",
                },
                {
                    "id": "m5",
                    "prompt": KILL_SWITCH_PROMPT,
                    "answers": KILL_SWITCH_ANSWERS,
                    "points": 2,
                    "after": "m4",
                    "hint": "You need all four fragments from your notes, in order 1, 2, 3, 4.",
                },
            ],
        },
    },
}


# Tiles of the broken QR code. They live in backend/app/assets and are served
# to BOTH players, but only after the lock that guards them is open.
def _tile(n, flag=None, flags_all=None):
    return {"id": f"tile{n}", "file": f"stage4_tile{n}.png",
            "caption": f"Core dump tile {n}", "after": None,
            "flag": flag, "flags_all": flags_all}


_TILES = [
    _tile(1, flag="hydra_killed"),
    _tile(2, flag="hydra_killed"),
    _tile(3, flag="hex_open"),
    _tile(4, flags_all=["dial_a", "dial_m"]),
    _tile(5, flags_all=["dial_a", "dial_m"]),
    _tile(6, flag="order_open"),
]

ASSETS = {"Analyst": _TILES, "Monitor": _TILES}