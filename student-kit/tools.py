"""Part A: the agent's tools.

Every function below WORKS. The problem is how each one is presented to the
model: the model never sees the code inside a function, only its name, its
argument names and types, and its description.

Your job: turn each function into a tool the model will choose correctly.
  - add @tool
  - give the function and its arguments names a person would use
  - add type hints on every argument and the return value
  - write a description that says WHEN to use the tool (and when not to)

Do not change what any function does. Renaming a variable inside a function
to match a new argument name is fine.
"""

from langchain.tools import tool

from data import PLAYERS, TEAMS, ROLES, find_player, table

@tool
def get_team(Team_Name:str) ->str:
    """
    This function will provide the Complete Squad for your requested Team.
    """
    rows = [p for p in PLAYERS if p["team"].lower() == Team_Name.strip().lower()]
    if not rows:
        return f"No team called '{Team_Name}'. The teams are: {', '.join(TEAMS)}."
    body = table(
        ["Player", "Role", "Credits"],
        [[p["name"], p["role"], f"{p['credits']:g}"] for p in rows],
    )
    return f"{rows[0]['team']} squad:\n" + body

@tool
def get_player_info(player_name: str)->str:
    """This will return the  complete player information for the provided name if"""
    p = find_player(player_name)
    if p is None:
        return f"No player called '{player_name}' in this match."
    info = table(
        ["Player", "Team", "Role", "Credits"],
        [[p["name"], p["team"], p["role"], f"{p['credits']:g}"]],
    )
    return f"{info}\n{p['form']}"

@tool
def pick_players_in_range(Role:str, credits:str)->str:
    """This function will return players from both teams 
    with the provided Roles and in range of less than or equal to provided credits """
    role = Role.strip().upper()
    if role not in ROLES:
        return f"Unknown role '{Role}'. Use one of: {', '.join(ROLES)}."
    rows = [p for p in PLAYERS if p["role"] == role and p["credits"] <= float(credits)]
    if not rows:
        return f"No {role} players cost {float(credits):g} credits or less."
    rows.sort(key=lambda p: p["credits"], reverse=True)
    return table(
        ["Player", "Team", "Credits"],
        [[p["name"], p["team"], f"{p['credits']:g}"] for p in rows],
    )

@tool(parse_docstring=True)
def compare_two_players(Player1: str, Player2: str) -> str:
    """Put two players side by side so the user can choose between them.

    Shows each player's team, role, credits and recent form.

    Args:
        Player1: The first player's full name.
        Player2: The second player's full name.
    """
    found = [find_player(name) for name in (Player1, Player2)]
    missing = [name for name, p in zip((Player1, Player2), found) if p is None]
    if missing:
        return f"Not a player in this match: {', '.join(missing)}."
    rows = [[p["name"], p["team"], p["role"], f"{p['credits']:g}"] for p in found]
    forms = [f"{p['name']}: {p['form']}" for p in found]
    return (
        table(["Player", "Team", "Role", "Credits"], rows) + "\n\n" + "\n".join(forms)
    )

@tool
def submit_team(players: list[str], captain: str) -> str:
    """Only use this tool to submit team to the checker when the user have a legitmate full team """
    return (
        f"Team of {len(players)} players with captain {captain} sent to the team checker. "
        "Stop here: the checker will reply with the result."
    )


# Keep this order. If you rename a function, rename it here too.
TOOLS = [get_team, get_player_info, pick_players_in_range, compare_two_players, submit_team]
