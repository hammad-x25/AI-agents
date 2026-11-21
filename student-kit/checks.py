"""The team rules, checked in plain code. Given: you do not need to change this file.

The model never decides whether a team is valid. This file does.
"""

from collections import Counter

from data import PLAYERS, find_player, table

TEAM_SIZE = 11
MAX_CREDITS = 100.0
MAX_FROM_ONE_SIDE = 7
ROLE_LIMITS = {"WK": (1, 4), "BAT": (3, 6), "AR": (1, 4), "BOWL": (3, 6)}
ROLE_NAMES = {"WK": "wicket-keepers", "BAT": "batters", "AR": "all-rounders", "BOWL": "bowlers"}

RULES = (
    f"exactly {TEAM_SIZE} players, at most {MAX_CREDITS:g} credits, "
    f"at most {MAX_FROM_ONE_SIDE} from one side, 1-4 wicket-keepers, 3-6 batters, "
    "1-4 all-rounders, 3-6 bowlers, and the captain must be one of the eleven"
)


def validate_team(players: list[str], captain: str) -> list[str]:
    """Return every rule the team breaks. An empty list means the team is valid."""
    problems = []

    unknown = [name for name in players if find_player(name) is None]
    if unknown:
        problems.append(f"These are not players in this match: {', '.join(unknown)}.")
    found = [find_player(name) for name in players if find_player(name) is not None]

    names = [p["name"] for p in found]
    repeated = sorted({n for n in names if names.count(n) > 1})
    if repeated:
        problems.append(f"Picked more than once: {', '.join(repeated)}.")

    if len(players) != TEAM_SIZE:
        problems.append(f"The team has {len(players)} players; it must have exactly {TEAM_SIZE}.")

    total = sum(p["credits"] for p in found)
    if total > MAX_CREDITS:
        problems.append(f"The team costs {total:g} credits; the limit is {MAX_CREDITS:g}.")

    for team, count in Counter(p["team"] for p in found).items():
        if count > MAX_FROM_ONE_SIDE:
            problems.append(f"{count} players are from {team}; at most {MAX_FROM_ONE_SIDE} may come from one side.")

    roles = Counter(p["role"] for p in found)
    for role, (low, high) in ROLE_LIMITS.items():
        if not low <= roles[role] <= high:
            problems.append(f"The team has {roles[role]} {ROLE_NAMES[role]}; it needs {low} to {high}.")

    if find_player(captain) is None or find_player(captain)["name"] not in names:
        problems.append(f"The captain ({captain}) must be one of the eleven players.")

    return problems


def team_sheet(players: list[str], captain: str) -> str:
    """The final team, written out by code (only called for a valid team)."""
    found = [find_player(name) for name in players]
    captain_name = find_player(captain)["name"]
    rows = []
    for role in ROLE_LIMITS:
        for p in found:
            if p["role"] == role:
                mark = " (C)" if p["name"] == captain_name else ""
                rows.append([role, p["name"] + mark, p["team"], f"{p['credits']:g}"])
    sheet = table(["Role", "Player", "Team", "Credits"], rows)
    width = max(len(line) for line in sheet.splitlines())
    total = f"Total: {sum(p['credits'] for p in found):g} / {MAX_CREDITS:g} credits"
    return "Your team is valid and locked in:\n\n" + sheet + "\n" + "-" * width + "\n" + total.rjust(width)
