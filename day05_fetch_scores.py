"""
day05_fetch_scores.py

Fetches NBA scoreboard from ESPN API and prints team names, scores, and game status.
"""

import requests

SCOREBOARD_URL = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard"


def fetch_scoreboard() -> dict:
    """Fetch scoreboard JSON from ESPN."""
    resp = requests.get(SCOREBOARD_URL)
    resp.raise_for_status()
    return resp.json()


def format_status(status: dict) -> str:
    """Build status string: quarter and time remaining, or scheduled/final description."""
    desc = status.get("type", {}).get("description", "")
    period = status.get("period", 0)
    clock = status.get("displayClock", "")

    if period and period > 0:
        # In progress or ended with period info
        quarter = f"Q{period}" if period <= 4 else f"OT{period - 4}"
        if clock:
            return f"{quarter} - {clock}"
        return f"{quarter}"
    # Scheduled, Final, or other
    detail = status.get("type", {}).get("shortDetail") or desc
    return detail or "—"


def print_games(data: dict) -> None:
    """Print team names, scores, and status for each game."""
    events = data.get("events", [])
    if not events:
        print("No games found.")
        return

    for event in events:
        comps = event.get("competitions", [])
        if not comps:
            continue
        comp = comps[0]
        competitors = comp.get("competitors", [])
        status = comp.get("status", {})

        # Order: away first, then home
        teams = sorted(competitors, key=lambda c: (0 if c.get("homeAway") == "away" else 1))
        away = teams[0]
        home = teams[1] if len(teams) > 1 else away

        away_name = away.get("team", {}).get("displayName", "?")
        home_name = home.get("team", {}).get("displayName", "?")
        away_score = away.get("score", "0")
        home_score = home.get("score", "0")
        status_str = format_status(status)

        print(f"{away_name}  {away_score}  @  {home_name}  {home_score}")
        print(f"  Status: {status_str}")
        print()


def main() -> None:
    data = fetch_scoreboard()
    print_games(data)


if __name__ == "__main__":
    main()
