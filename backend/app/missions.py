"""Fictional, server-authored mission content and answer keys."""

# Keep answer_key out of all public response builders. Only the currently
# unlocked stage is selected for a player, so later-stage details stay private.
MISSIONS = {
    1: {
        "title": "The Hydra Alert",
        "roles": {
            "Analyst": {
                "instructions": "Review the fictional endpoint notes and identify the alert's named threat.",
                "evidence": [
                    "NovaCorp workstation note: scheduled item 'Hydra_Update' appeared at 09:14.",
                    "Sandbox report: the file was quarantined before it ran.",
                ],
                "question": "What threat name appears in the alert?",
                "answer_key": "hydra",
            },
            "Monitor": {
                "instructions": "Review the simulated message and alert. Identify the threat name in the alert.",
                "evidence": [
                    "Training email: 'Urgent Hydra security update' from updates@novacorp.invalid.",
                    "Gateway alert: attachment blocked; no external connection was made.",
                ],
                "question": "What threat name appears in the alert?",
                "answer_key": "hydra",
            },
        },
    },
    2: {
        "title": "The Quiet Connection",
        "roles": {
            "Analyst": {
                "instructions": "Use the fictional log entries to identify the account that opened the quarantined note.",
                "evidence": [
                    "Lab log: 09:12 local — user avery.park opened case note NC-204.",
                    "Lab log: 09:14 local — Hydra_Update quarantined before execution.",
                ],
                "question": "Which account opened case note NC-204?",
                "answer_key": "avery.park",
            },
            "Monitor": {
                "instructions": "Review the simulated gateway log and identify the blocked destination label.",
                "evidence": [
                    "Training gateway: simulated request to 198.51.100.24 labeled NC-204.",
                    "Disposition: reserved documentation address; request blocked in the simulation.",
                ],
                "question": "What case label is attached to the blocked request?",
                "answer_key": "nc-204",
            },
        },
    },
    3: {
        "title": "A Pattern in the Records",
        "roles": {
            "Analyst": {
                "instructions": "Compare the fictional access records and identify the account with repeated after-hours access.",
                "evidence": [
                    "Training audit: avery.park signed out at 17:02 on all reviewed days.",
                    "Training audit: jordan.lee accessed archive index at 22:11 on three reviewed days.",
                ],
                "question": "Which account has repeated after-hours archive access?",
                "answer_key": "jordan.lee",
            },
            "Monitor": {
                "instructions": "Compare simulated alert records and identify the repeated case label.",
                "evidence": [
                    "Training alerts: NC-204 appears in three separate archive-index notices.",
                    "All listed destinations use reserved documentation ranges and are non-routable in this game.",
                ],
                "question": "Which case label repeats in the archive-index notices?",
                "answer_key": "nc-204",
            },
        },
    },
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


def public_mission(stage: int, role: str) -> dict:
    mission = MISSIONS[stage]
    return {
        "stage": stage,
        "title": mission["title"],
        "role": role,
        "instructions": mission["roles"][role]["instructions"],
        "evidence": mission["roles"][role]["evidence"],
        "question": mission["roles"][role]["question"],
    }
