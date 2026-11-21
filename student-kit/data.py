"""Match data for tonight's game. Given: you do not need to change this file.

Squads: the Lahore Qalandars and Karachi Kings squads for PSL 2026 (all 18 players
each, including the ones who usually sit on the bench), from ESPNcricinfo.
Credits and recent form are MADE UP for this activity: they are not real prices
or real statistics.
Roles: WK = wicket-keeper, BAT = batter, AR = all-rounder, BOWL = bowler.
"""

MATCH = "Lahore Qalandars vs Karachi Kings"

PLAYERS = [
    # Lahore Qalandars (18 players)
    {"name": "Haseebullah Khan", "team": "Lahore Qalandars", "role": "WK", "credits": 9.0, "form": "Last 5 innings: 21, 22, 55, 1, 40"},
    {"name": "Rubin Hermann", "team": "Lahore Qalandars", "role": "WK", "credits": 7.5, "form": "Last 5 innings: 0, 46, 29, 50, 17"},
    {"name": "Fakhar Zaman", "team": "Lahore Qalandars", "role": "BAT", "credits": 10.5, "form": "Last 5 innings: 67, 54, 46, 62, 37"},
    {"name": "Abdullah Shafique", "team": "Lahore Qalandars", "role": "BAT", "credits": 9.0, "form": "Last 5 innings: 36, 55, 44, 35, 82"},
    {"name": "Parvez Hossain Emon", "team": "Lahore Qalandars", "role": "BAT", "credits": 8.0, "form": "Last 5 innings: 32, 21, 34, 22, 24"},
    {"name": "Asif Ali", "team": "Lahore Qalandars", "role": "BAT", "credits": 8.0, "form": "Last 5 innings: 25, 68, 32, 35, 44"},
    {"name": "Muhammad Naeem", "team": "Lahore Qalandars", "role": "BAT", "credits": 7.5, "form": "Last 5 innings: 62, 22, 15, 70, 0"},
    {"name": "Tayyab Tahir", "team": "Lahore Qalandars", "role": "BAT", "credits": 7.0, "form": "Last 5 innings: 14, 32, 61, 3, 0"},
    {"name": "Mohammad Farooq", "team": "Lahore Qalandars", "role": "BAT", "credits": 7.0, "form": "Last 5 innings: 32, 11, 13, 28, 24"},
    {"name": "Sikandar Raza", "team": "Lahore Qalandars", "role": "AR", "credits": 10.0, "form": "Last 5: 39 runs & 1 wkt, 51 runs & 3 wkts, 36 runs & 1 wkt, 45 runs & 2 wkts, 23 runs & 1 wkt"},
    {"name": "Dasun Shanaka", "team": "Lahore Qalandars", "role": "AR", "credits": 8.5, "form": "Last 5: 37 runs & 1 wkt, 21 runs & 1 wkt, 24 runs & 1 wkt, 1 runs & 3 wkts, 27 runs & 0 wkts"},
    {"name": "Gudakesh Motie", "team": "Lahore Qalandars", "role": "AR", "credits": 8.0, "form": "Last 5: 33 runs & 1 wkt, 21 runs & 2 wkts, 48 runs & 2 wkts, 40 runs & 3 wkts, 8 runs & 1 wkt"},
    {"name": "Hussain Talat", "team": "Lahore Qalandars", "role": "AR", "credits": 7.0, "form": "Last 5: 23 runs & 0 wkts, 10 runs & 2 wkts, 26 runs & 1 wkt, 0 runs & 3 wkts, 20 runs & 1 wkt"},
    {"name": "Shaheen Afridi", "team": "Lahore Qalandars", "role": "BOWL", "credits": 10.0, "form": "Last 5 matches wickets: 3, 1, 1, 1, 5 (economy 7.2)"},
    {"name": "Haris Rauf", "team": "Lahore Qalandars", "role": "BOWL", "credits": 9.5, "form": "Last 5 matches wickets: 1, 2, 2, 3, 3 (economy 7.5)"},
    {"name": "Mustafizur Rahman", "team": "Lahore Qalandars", "role": "BOWL", "credits": 9.0, "form": "Last 5 matches wickets: 2, 1, 0, 2, 2 (economy 7.8)"},
    {"name": "Usama Mir", "team": "Lahore Qalandars", "role": "BOWL", "credits": 8.0, "form": "Last 5 matches wickets: 3, 1, 1, 2, 0 (economy 8.6)"},
    {"name": "Ubaid Shah", "team": "Lahore Qalandars", "role": "BOWL", "credits": 7.5, "form": "Last 5 matches wickets: 0, 0, 2, 4, 2 (economy 8.9)"},
    # Karachi Kings (18 players)
    {"name": "Johnson Charles", "team": "Karachi Kings", "role": "WK", "credits": 8.5, "form": "Last 5 innings: 58, 41, 42, 29, 32"},
    {"name": "Azam Khan", "team": "Karachi Kings", "role": "WK", "credits": 8.0, "form": "Last 5 innings: 0, 10, 8, 46, 43"},
    {"name": "Saad Baig", "team": "Karachi Kings", "role": "WK", "credits": 7.0, "form": "Last 5 innings: 41, 48, 15, 39, 55"},
    {"name": "David Warner", "team": "Karachi Kings", "role": "BAT", "credits": 10.5, "form": "Last 5 innings: 59, 79, 57, 30, 62"},
    {"name": "Muhammad Waseem", "team": "Karachi Kings", "role": "BAT", "credits": 8.5, "form": "Last 5 innings: 22, 39, 29, 43, 0"},
    {"name": "Aqib Ilyas", "team": "Karachi Kings", "role": "BAT", "credits": 7.5, "form": "Last 5 innings: 63, 50, 19, 9, 26"},
    {"name": "Moeen Ali", "team": "Karachi Kings", "role": "AR", "credits": 10.0, "form": "Last 5: 44 runs & 2 wkts, 41 runs & 0 wkts, 22 runs & 3 wkts, 39 runs & 0 wkts, 25 runs & 0 wkts"},
    {"name": "Salman Ali Agha", "team": "Karachi Kings", "role": "AR", "credits": 10.0, "form": "Last 5: 23 runs & 3 wkts, 33 runs & 3 wkts, 38 runs & 0 wkts, 28 runs & 4 wkts, 26 runs & 1 wkt"},
    {"name": "Khushdil Shah", "team": "Karachi Kings", "role": "AR", "credits": 7.5, "form": "Last 5: 32 runs & 1 wkt, 17 runs & 2 wkts, 0 runs & 1 wkt, 4 runs & 0 wkts, 7 runs & 2 wkts"},
    {"name": "Shahid Aziz", "team": "Karachi Kings", "role": "AR", "credits": 7.0, "form": "Last 5: 12 runs & 0 wkts, 0 runs & 2 wkts, 26 runs & 0 wkts, 43 runs & 0 wkts, 0 runs & 1 wkt"},
    {"name": "Hasan Ali", "team": "Karachi Kings", "role": "BOWL", "credits": 10.0, "form": "Last 5 matches wickets: 4, 5, 4, 2, 2 (economy 7.2)"},
    {"name": "Adam Zampa", "team": "Karachi Kings", "role": "BOWL", "credits": 10.0, "form": "Last 5 matches wickets: 1, 3, 2, 3, 1 (economy 7.2)"},
    {"name": "Abbas Afridi", "team": "Karachi Kings", "role": "BOWL", "credits": 8.5, "form": "Last 5 matches wickets: 1, 1, 0, 0, 1 (economy 8.2)"},
    {"name": "Mir Hamza", "team": "Karachi Kings", "role": "BOWL", "credits": 8.0, "form": "Last 5 matches wickets: 0, 2, 2, 0, 2 (economy 8.6)"},
    {"name": "Ihsanullah", "team": "Karachi Kings", "role": "BOWL", "credits": 7.5, "form": "Last 5 matches wickets: 2, 3, 1, 1, 0 (economy 8.9)"},
    {"name": "Mohammad Hamza Sohail", "team": "Karachi Kings", "role": "BOWL", "credits": 7.0, "form": "Last 5 matches wickets: 1, 1, 1, 1, 2 (economy 9.2)"},
    {"name": "Khuzaima bin Tanveer", "team": "Karachi Kings", "role": "BOWL", "credits": 7.0, "form": "Last 5 matches wickets: 1, 1, 0, 1, 0 (economy 9.2)"},
    {"name": "Rizwanullah", "team": "Karachi Kings", "role": "BOWL", "credits": 7.0, "form": "Last 5 matches wickets: 0, 1, 3, 2, 1 (economy 9.2)"},
]

TEAMS = sorted({p["team"] for p in PLAYERS})
ROLES = ["WK", "BAT", "AR", "BOWL"]


def find_player(name: str) -> dict | None:
    """Look a player up by name, ignoring case and extra spaces."""
    wanted = " ".join(name.split()).lower()
    for p in PLAYERS:
        if p["name"].lower() == wanted:
            return p
    return None


def table(headers: list[str], rows: list[list], right: tuple = ("Credits",)) -> str:
    """Lay rows out as a plain-text table with lined-up columns (for the terminal)."""
    cells = [[str(c) for c in row] for row in rows]
    widths = [max(len(h), *(len(r[i]) for r in cells)) if cells else len(h)
              for i, h in enumerate(headers)]

    def line(values):
        out = [v.rjust(w) if h in right else v.ljust(w) for v, w, h in zip(values, widths, headers)]
        return "  ".join(out).rstrip()

    return "\n".join([line(headers), line(["-" * w for w in widths])] + [line(r) for r in cells])
