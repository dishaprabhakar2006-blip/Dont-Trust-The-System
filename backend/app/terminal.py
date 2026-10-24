"""Server-side fake terminal.

Files live here, never in the browser. A file (or command) can be locked
behind a question id ("after"): it only exists for that player once they
have answered that question. Everything is read-only.
"""

import posixpath
import re
import shlex

MAX_OUTPUT = 4000

HELP_TEXT = """Commands:
  help                       show this list
  ls [-a] [path]             list files (-a also shows hidden ones)
  cd <path>                  change folder (cd .. goes up, cd / goes to the top)
  pwd                        show where you are
  cat <file>                 print a file
  grep <word> <file>         show the lines that contain a word
  cat <file> | grep <word>   same thing, pipe style
  whoami                     show who you are
  clear                      clear the screen"""


def _f(text: str, after: str | None = None) -> dict:
    return {"text": text, "after": after}


TERMINALS = {
    2: {
        "Analyst": {
            "host": "nova-db02",
            "files": {
                "/README.txt": _f(
                    "NOVA-DB02 admin console\n"
                    "Logged in as: admin\n"
                    "Attackers hide things. Hidden files and folders start with a dot.\n"
                    "Type 'help' for commands."
                ),
                "/etc/motd": _f("NovaCorp internal system. Authorised use only."),
                "/var/log/syslog": _f(
                    "14 Oct 03:00:01 cron: nightly job ok\n"
                    "14 Oct 09:14:02 av: Hydra_Update quarantined\n"
                    "14 Oct 09:15:30 cron: cache cleanup skipped"
                ),
                "/home/avery.park/todo.txt": _f(
                    "renew parking permit\nsubmit expense report\nlunch with maria"
                ),
                "/home/maria.dsouza/maint.txt": _f(
                    "maintenance window 02:30 approved by IT. routine patching."
                ),
                                "/home/priya.nair/notes.txt": _f("team lunch friday. book room 4B for the review."),
                "/home/ben.carter/todo.txt": _f("update rota\norder new badges\nreply to HR"),
                "/home/maria.dsouza/.bash_history": _f("sudo apt update\nsudo apt upgrade\nexit"),
                "/home/.mozilla_old/cache.tmp": _f("browser cache. nothing useful here."),
                "/home/.cache_old/readme.tmp": _f(
                    "cleanup scheduled. do not trust the banner."
                ),
                "/home/.cache_old/.old_session": _f("session token expired."),
                "/home/.cache_old/vault.bin": _f(
                    "== NOVA VAULT v2 ==\n"
                    "STATE: LOCKED\n"
                    "SECURITY QUESTION:\n"
                    "  Which user logged in at 03:07 AM from an unknown IP?\n"
                    "Answer format: username\n"
                    "(Type the answer in your Mission panel. "
                    "Login records are not stored on this server.)"
                ),
                "/home/.cache_old/vault/fragment2.txt": _f(
                    "FRAGMENT 2: KS-19C4", after="a2"
                ),
                "/home/.cache_old/vault/note.enc": _f(
                    "VAULT NOTE (encrypted)\n"
                    "Cipher: Caesar. The attacker always used the same shift.\n"
                    "His scratchpad has the number. Your partner can reach it.\n"
                    "\n"
                    "WDVN DUFKLYHLQGHA UXQV DIWHU FOHDQXS",
                    after="a2",
                ),
            },
        },
        "Monitor": {
            "host": "nova-siem",
            "files": {
                "/README.txt": _f(
                    "NOVA-SIEM log viewer\n"
                    "Logged in as: monitor\n"
                    "Logs are in /logs and settings are in /config.\n"
                    "Type 'help' for commands."
                ),
                "/logs/logins.txt": _f(
                    "\n".join([
                        "DATE    TIME      USER            SOURCE IP     EVENT",
                        "13 Oct  00:12:44  backup-agent    10.0.4.9      heartbeat",
                        "13 Oct  03:07:55  backup-agent    10.0.4.9      heartbeat",
                        "13 Oct  06:58:20  maria.dsouza    10.0.4.50     login ok",
                        "13 Oct  07:41:09  avery.park      10.0.4.21     login ok",
                        "13 Oct  08:15:33  contractor.ray  10.0.9.14     vpn login ok",
                        "13 Oct  09:02:47  priya.nair      10.0.4.33     login ok",
                        "13 Oct  09:30:12  avery.park      10.0.4.21     file access /finance/q3.xlsx",
                        "13 Oct  10:11:58  ben.carter      10.0.4.62     login ok",
                        "13 Oct  11:07:21  priya.nair      10.0.4.33     password changed",
                        "13 Oct  12:45:00  maria.dsouza    10.0.4.50     logout",
                        "13 Oct  13:07:44  ben.carter      10.0.4.62     file access /hr/policies.pdf",
                        "13 Oct  14:20:16  contractor.ray  10.0.9.14     vpn logout",
                        "13 Oct  17:02:14  avery.park      10.0.4.21     logout",
                        "13 Oct  18:30:55  priya.nair      10.0.4.33     logout",
                        "13 Oct  21:48:30  admin           192.0.2.55    login FAILED (3 attempts)",
                        "13 Oct  22:41:07  avery.park      10.0.4.21     login ok",
                        "13 Oct  23:07:12  backup-agent    10.0.4.9      heartbeat",
                        "13 Oct  23:55:40  avery.park      10.0.4.21     logout",
                        "14 Oct  00:12:45  backup-agent    10.0.4.9      heartbeat",
                        "14 Oct  01:30:18  admin           198.51.100.8  login FAILED (2 attempts)",
                        "14 Oct  02:00:03  backup-agent    10.0.4.9      nightly backup started",
                        "14 Oct  02:30:00  maria.dsouza    10.0.4.50     login ok (maintenance window, approved)",
                        "14 Oct  02:58:41  maria.dsouza    10.0.4.50     patch applied",
                        "14 Oct  03:07:30  contractor.ray  10.0.9.14     vpn login ok",
                        "14 Oct  03:07:41  svc_backup01    203.0.113.77  session opened",
                        "14 Oct  03:12:09  maria.dsouza    10.0.4.50     logout",
                        "14 Oct  03:17:22  backup-agent    10.0.4.9      heartbeat",
                        "14 Oct  04:45:10  contractor.ray  10.0.9.14     vpn logout",
                        "14 Oct  06:50:27  maria.dsouza    10.0.4.50     login ok",
                        "14 Oct  08:41:19  ben.carter      10.0.4.62     login ok",
                        "14 Oct  09:02:11  avery.park      10.0.4.21     login ok",
                        "14 Oct  09:14:03  priya.nair      10.0.4.33     login ok",
                        "14 Oct  09:58:36  ben.carter      10.0.4.62     file access /hr/rota.xlsx",
                        "14 Oct  10:21:50  priya.nair      10.0.4.33     logout",
                        "14 Oct  11:07:48  contractor.ray  10.0.9.14     vpn login ok",
                        "14 Oct  12:30:02  avery.park      10.0.4.21     file access /finance/q3.xlsx",
                        "14 Oct  13:07:15  jordan.lee      10.0.4.35     login ok",
                        "14 Oct  15:44:21  ben.carter      10.0.4.62     logout",
                    ])
                ),
                "/logs/firewall.txt": _f(
                    "\n".join([
                        "13 Oct 08:15:40 ALLOW 10.0.9.14 -> vpn-gw port 1194 (vpn)",
                        "13 Oct 09:30:12 ALLOW 10.0.4.21 -> fileserver port 445",
                        "13 Oct 21:48:31 BLOCK 192.0.2.55 -> nova-db02 port 22 (ssh)",
                        "14 Oct 01:30:19 BLOCK 198.51.100.8 -> nova-db02 port 22 (ssh)",
                        "14 Oct 03:07:42 ALLOW 203.0.113.77 -> nova-db02 port 22 (ssh)",
                        "14 Oct 03:11:09 ALLOW 203.0.113.77 -> nova-db02 port 22 (ssh)",
                        "14 Oct 03:15:55 ALLOW 203.0.113.77 -> nova-db02 port 443 (https)",
                        "14 Oct 09:14:03 BLOCK nova-ws12 -> 198.51.100.24 (Hydra_Update quarantined)",
                        "14 Oct 11:30:00 ALLOW 10.0.4.21 -> intranet port 443",
                    ])
                ),
                "/logs/backup.txt": _f(
                    "14 Oct 02:00:00 nightly backup ok"
                ),
                "/config/known_networks.txt": _f(
                    "KNOWN NETWORKS (NovaCorp IT)\n"
                    "10.0.4.0/24   office LAN\n"
                    "10.0.9.0/24   staff VPN pool\n"
                    "10.0.4.9      backup-agent (approved)\n"
                    "Everything else is UNKNOWN / external."
                ),
                "/audit/accounts.txt": _f(
                    "\n".join([
                        "ACCOUNT AUDIT (system vs HR)",
                        "USER            CREATED      HR REQUEST",
                        "avery.park      2019-03-04   on file",
                        "jordan.lee      2021-06-14   on file",
                        "maria.dsouza    2022-01-10   on file",
                        "backup-agent    2023-05-02   on file",
                        "contractor.ray  2026-09-01   on file (contract)",
                        "svc_backup01    2026-10-02   NONE",
                    ]),
                    after="m1",
                ),
                "/config/scratchpad.txt": _f(
                    "ATTACKER SCRATCHPAD\n"
                    "remember: my caesar shift is 3\n"
                    "same shift for every note. do not forget.",
                    after="m1",
                ),
            },
        },
    },
}

def has_terminal(stage: int, role: str) -> bool:
    return role in TERMINALS.get(stage, {})


def _open(item: dict, answered: dict, stage: int, role: str) -> bool:
    after = item.get("after")
    return after is None or bool(answered.get(f"{stage}:{role}:{after}"))


def _abs(cwd: str, path: str) -> str:
    if path.startswith("~"):
        path = "/home" + path[1:]
    if not path.startswith("/"):
        path = posixpath.join(cwd, path)
    path = re.sub(r"/+", "/", path)
    return posixpath.normpath(path)


def _is_dir(files: dict, path: str) -> bool:
    if path == "/":
        return True
    prefix = path.rstrip("/") + "/"
    return any(p.startswith(prefix) for p in files)


def _list_dir(files: dict, path: str, show_all: bool) -> list[str]:
    prefix = path.rstrip("/") + "/"
    names = set()
    for p in files:
        if p.startswith(prefix):
            rest = p[len(prefix):]
            name = rest.split("/")[0]
            if name.startswith(".") and not show_all:
                continue
            names.add(name + "/" if "/" in rest else name)
    return sorted(names)


def _single(text: str, term: dict, files: dict, extras: dict, cwd: str, role: str):
    try:
        parts = shlex.split(text)
    except ValueError:
        return "bash: syntax error (check your quotes)", cwd
    if not parts:
        return "", cwd

    cmd, args = parts[0].lower(), parts[1:]
    flags = [a for a in args if a.startswith("-")]
    rest = [a for a in args if not a.startswith("-")]
    out = ""

    if cmd == "help":
        out = HELP_TEXT
        if extras:
            out += "\n  " + ", ".join(sorted(extras)) + "   (extra commands)"
    elif cmd == "clear":
        out = ""
    elif cmd == "pwd":
        out = cwd
    elif cmd == "whoami":
        out = f"{role.lower()}@{term['host']}"
    elif cmd == "cd":
        target = _abs(cwd, rest[0]) if rest else "/"
        if _is_dir(files, target):
            cwd = target
        else:
            out = f"cd: {rest[0]}: No such directory"
    elif cmd == "ls":
        show_all = any("a" in f for f in flags)
        target = _abs(cwd, rest[0]) if rest else cwd
        if target in files:
            out = posixpath.basename(target)
        elif _is_dir(files, target):
            out = "\n".join(_list_dir(files, target, show_all))
        else:
            shown = rest[0] if rest else target
            out = f"ls: cannot access '{shown}': No such file or directory"
    elif cmd == "cat":
        if not rest:
            out = "cat: missing file name"
        else:
            chunks = []
            for name in rest:
                target = _abs(cwd, name)
                if target in files:
                    chunks.append(files[target])
                elif _is_dir(files, target):
                    chunks.append(f"cat: {name}: Is a directory")
                else:
                    chunks.append(f"cat: {name}: No such file or directory")
            out = "\n".join(chunks)
    elif cmd == "grep":
        if len(rest) < 2:
            out = "usage: grep <word> <file>"
        else:
            word, name = rest[0].lower(), rest[1]
            target = _abs(cwd, name)
            if target in files:
                out = "\n".join(
                    line for line in files[target].splitlines() if word in line.lower()
                )
            else:
                out = f"grep: {name}: No such file or directory"
    elif cmd in extras:
        out = extras[cmd]
    else:
        out = f"bash: {cmd}: command not found. Type 'help'."

    return out, cwd


def _pipe_grep(text: str, previous: str) -> str:
    try:
        parts = shlex.split(text)
    except ValueError:
        return "bash: syntax error (check your quotes)"
    parts = [p for p in parts if not p.startswith("-")]
    if len(parts) != 2 or parts[0].lower() != "grep":
        return "bash: after the | only 'grep <word>' works here"
    word = parts[1].lower()
    return "\n".join(l for l in previous.splitlines() if word in l.lower())


def run_command(stage: int, role: str, answered: dict, command: str, cwd: str):
    """Return (output, new_cwd, prompt)."""
    term = TERMINALS.get(stage, {}).get(role)
    if term is None:
        return "No terminal on this screen. Use your evidence panel.", "/", "$ "

    files = {
        p: f["text"] for p, f in term["files"].items() if _open(f, answered, stage, role)
    }
    extras = {
        n: c["text"]
        for n, c in term.get("commands", {}).items()
        if _open(c, answered, stage, role)
    }

    cwd = _abs("/", cwd or "/")
    if not _is_dir(files, cwd):
        cwd = "/"

    def prompt(c: str) -> str:
        return f"{role.lower()}@{term['host']}:{c}$ "

    segments = command.split("|")
    if len(segments) > 2:
        return "bash: only one pipe (|) is supported here", cwd, prompt(cwd)

    out, cwd = _single(segments[0], term, files, extras, cwd, role)
    if len(segments) == 2:
        out = _pipe_grep(segments[1], out)

    return out[:MAX_OUTPUT], cwd, prompt(cwd)