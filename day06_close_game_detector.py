import json
import os
import re
import sys
import time

import requests

NBA_SCOREBOARD_URL = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard"
NCAA_SCOREBOARD_URL = "https://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/scoreboard"
PUSHOVER_URL = "https://api.pushover.net/1/messages.json"
CHECK_INTERVAL = 5
MAX_MINUTES = 5
MAX_SCORE_DIFF = 5
AP_TOP_25_MAX = 25  # College: only alert if at least one team is ranked this or better
# ESPN's tournamentId for the main NCAA Tournament (March Madness). NIT/CBI/conference use other IDs.
NCAA_MAIN_TOURNAMENT_ID = 22

# Pushover (optional — set to None to disable). Env vars override for cloud/scheduled runs.
PUSHOVER_APP_TOKEN = os.environ.get("PUSHOVER_APP_TOKEN") or "a7w3uqzjsyp5iuw3hmjdpvh4gb8iu4"
PUSHOVER_USER_KEY = os.environ.get("PUSHOVER_USER_KEY") or "udhkmqdag5zjgm2r9k2ay3x51zf8r1"

# Game IDs we've already sent an alert for — only one alert per game
alerted_games = set()

# For --once mode: persist alerted_games so scheduled runs don't double-alert
_script_dir = os.path.dirname(os.path.abspath(__file__))
STATE_DIR = os.path.join(_script_dir, ".state")
STATE_FILE = os.path.join(STATE_DIR, "close_game_alerted.json")


def load_alerted_games():
    """Load alerted game keys from disk (for scheduled/one-shot runs)."""
    global alerted_games
    try:
        if os.path.isfile(STATE_FILE):
            with open(STATE_FILE) as f:
                data = json.load(f)
                alerted_games = set(data) if isinstance(data, list) else set()
    except (json.JSONDecodeError, OSError):
        alerted_games = set()


def save_alerted_games():
    """Save alerted game keys to disk."""
    try:
        os.makedirs(STATE_DIR, exist_ok=True)
        with open(STATE_FILE, "w") as f:
            json.dump(list(alerted_games), f)
    except OSError:
        pass


def send_pushover(title: str, message: str) -> None:
    """Send a notification via Pushover. No-op if credentials not set."""
    if not PUSHOVER_APP_TOKEN or not PUSHOVER_USER_KEY:
        return
    try:
        requests.post(
            PUSHOVER_URL,
            data={
                "token": PUSHOVER_APP_TOKEN,
                "user": PUSHOVER_USER_KEY,
                "message": message,
                "title": title,
            },
            timeout=10,
        )
    except requests.RequestException:
        pass  # Don't break the loop if push fails


def clock_string_to_minutes(clock_str):
    """Convert '2:34' (M:SS) to minutes as float. Returns None if invalid."""
    if not clock_str or not isinstance(clock_str, str):
        return None
    m = re.match(r"^(\d+):(\d{2})$", clock_str.strip())
    if not m:
        return None
    return int(m.group(1)) + int(m.group(2)) / 60.0


def get_minutes_remaining_in_period(status):
    """Time remaining in the *current period* (quarter/half) in minutes. None if unknown."""
    period = status.get("period", 0)
    if not period or period <= 0:
        return None
    clock_sec = status.get("clock")
    if clock_sec is not None:
        try:
            return float(clock_sec) / 60.0
        except (TypeError, ValueError):
            pass
    return clock_string_to_minutes(status.get("displayClock", "") or "")


def is_in_final_period(status, is_college):
    """
    True if we're in the period where 'time left' = time left in game (or OT).
    NBA: Q4 or OT (period >= 4). NCAA: 2nd half or OT (period >= 2).
    ESPN's clock is per-period, so we only alert in these periods.
    """
    period = status.get("period", 0) or 0
    if is_college:
        return period >= 2  # 2nd half or OT
    return period >= 4  # Q4 or OT


def format_quarter(status):
    """NBA: Q1, Q4, OT1 from status.period."""
    period = status.get("period", 0) or 0
    if period <= 4:
        return f"Q{period}"
    return f"OT{period - 4}"


def format_period_college(status):
    """College (halves): 1st Half, 2nd Half, OT1, OT2 ... from status.period."""
    period = status.get("period", 0) or 0
    if period == 1:
        return "1st Half"
    if period == 2:
        return "2nd Half"
    if period >= 3:
        return f"OT{period - 2}"
    return "?"


def is_ncaa_tournament(data):
    """True if the NCAA scoreboard is for postseason (tournament), not regular season."""
    leagues = data.get("leagues", [])
    if not leagues:
        return False
    season = leagues[0].get("season", {})
    stype = season.get("type", {})
    # type 3 = Postseason, abbreviation "post" (type can be int or string from API)
    t = stype.get("type")
    if t == 3 or t == "3":
        return True
    return (stype.get("abbreviation") or "").lower() == "post"


def is_ncaa_main_tournament_game(game):
    """True if this game is part of the main NCAA Tournament (March Madness)."""
    comps = game.get("competitions", [])
    if not comps:
        return False
    comp = comps[0]
    tid = comp.get("tournamentId")
    if tid is not None and (tid == NCAA_MAIN_TOURNAMENT_ID or tid == str(NCAA_MAIN_TOURNAMENT_ID)):
        return True
    for note in comp.get("notes", []) or []:
        headline = (note.get("headline") or "").lower()
        if "men's basketball championship" in headline:
            return True
    return False


def is_conference_tournament_game(game):
    """True if this game is part of a conference tournament (e.g. Big Ten, SEC, ACC)."""
    comps = game.get("competitions", [])
    if not comps:
        return False
    for note in comps[0].get("notes", []) or []:
        headline = (note.get("headline") or "").lower()
        # "Conference" + tournament/championship (e.g. "Atlantic 10 Conference Tournament")
        if "conference" in headline and ("tournament" in headline or "championship" in headline):
            return True
        # Major conferences often omit "conference" (e.g. "Big Ten Tournament", "SEC Tournament", "ACC Championship")
        if any(x in headline for x in ("big ten", "big 10", "big 12", "big xii", "sec tournament", "sec championship", "acc tournament", "acc championship")):
            return True
    return False


def is_ncaa_postseason_game_included(game):
    """True if we should include this postseason game: main NCAA Tournament or conference tournament (not NIT/CBI/etc)."""
    return is_ncaa_main_tournament_game(game) or is_conference_tournament_game(game)


def has_top25_team(competitors):
    """True if any competitor has AP Top 25 rank (curatedRank.current 1-25)."""
    for c in competitors:
        rank = c.get("curatedRank", {}).get("current")
        if rank is not None and 1 <= rank <= AP_TOP_25_MAX:
            return True
    return False


def get_team_label(competitor, use_seed=False, use_rank=False):
    """Team display name, optionally prefixed with #seed (tournament) or #rank (regular season)."""
    name = competitor.get("team", {}).get("displayName", "?")
    rank_or_seed = competitor.get("curatedRank", {}).get("current")
    if rank_or_seed is None:
        return name
    if use_seed and 1 <= rank_or_seed <= 16:
        return f"#{rank_or_seed} {name}"
    if use_rank and 1 <= rank_or_seed <= AP_TOP_25_MAX:
        return f"#{rank_or_seed} {name}"
    return name


def format_time_left(status):
    """Display clock string e.g. '2:34' or '0:00'. Empty if unknown."""
    return (status.get("displayClock") or "").strip() or "?"


def get_live_game_keys(events, league_key):
    """Return set of 'league_key:game_id' for games currently in progress (state == 'in')."""
    keys = set()
    for game in events:
        comps = game.get("competitions", [])
        if not comps:
            continue
        status = comps[0].get("status", {})
        if status.get("type", {}).get("state") != "in":
            continue
        gid = game.get("id")
        if gid:
            keys.add(f"{league_key}:{gid}")
    return keys


def process_league(data, league_key, is_college):
    """
    Process events for one league. league_key is 'nba' or 'ncaa' (for dedup).
    is_college: use halves; regular season requires at least one AP Top 25 team;
    tournament includes all close games and shows seed in notification when available.
    Returns number of close games (that we alerted on or had already alerted).
    """
    events = data.get("events", [])
    close_count = 0
    ncaa_tournament = is_college and is_ncaa_tournament(data)
    for game in events:
        comps = game.get("competitions", [])
        if not comps:
            continue
        comp = comps[0]
        status = comp.get("status", {})
        if status.get("type", {}).get("state") != "in":
            continue

        competitors = comp.get("competitors", [])
        # Regular season: only games with at least one Top 25 team.
        if is_college and not ncaa_tournament and not has_top25_team(competitors):
            continue
        # Postseason: main NCAA Tournament or conference tournaments only (not NIT/CBI/etc).
        if is_college and ncaa_tournament and not is_ncaa_postseason_game_included(game):
            continue
        teams = sorted(competitors, key=lambda c: (0 if c.get("homeAway") == "away" else 1))
        if len(teams) < 2:
            continue
        away, home = teams[0], teams[1]
        if is_college and ncaa_tournament:
            team_a = get_team_label(away, use_seed=True)
            team_b = get_team_label(home, use_seed=True)
        elif is_college:
            team_a = get_team_label(away, use_rank=True)
            team_b = get_team_label(home, use_rank=True)
        else:
            team_a = away.get("team", {}).get("displayName", "?")
            team_b = home.get("team", {}).get("displayName", "?")
        try:
            away_score = int(away.get("score") or "0")
            home_score = int(home.get("score") or "0")
        except (TypeError, ValueError):
            continue
        score_diff = abs(home_score - away_score)
        # ESPN clock is per-period; only treat as "final 5 min" in last period (Q4/2nd half) or OT
        if not is_in_final_period(status, is_college):
            continue
        minutes_in_period = get_minutes_remaining_in_period(status)
        if minutes_in_period is None:
            continue
        if minutes_in_period <= MAX_MINUTES and score_diff <= MAX_SCORE_DIFF:
            game_id = game.get("id") or ""
            alert_key = f"{league_key}:{game_id}" if game_id else ""
            if alert_key and alert_key not in alerted_games:
                period_str = format_period_college(status) if is_college else format_quarter(status)
                time_left = format_time_left(status)
                score_str = f"{away_score}-{home_score}"
                sport = "NCAA" if is_college else "NBA"
                msg = f"🔥 {team_a} vs {team_b} | {score_str} | {period_str} {time_left}"
                print(f"CLOSE GAME ({sport}): {msg}")
                send_pushover(f"Close Game ({sport})", msg)
                alerted_games.add(alert_key)
            close_count += 1
    return close_count


def run_one_check():
    """Fetch scoreboards, prune and process, return (nba_events, ncaa_events, nba_close, ncaa_close)."""
    global alerted_games
    nba_events, ncaa_events = [], []
    try:
        resp = requests.get(NBA_SCOREBOARD_URL, timeout=10)
        resp.raise_for_status()
        nba_events = resp.json().get("events", [])
    except requests.RequestException as e:
        print("Could not fetch NBA scoreboard:", e)
    ncaa_data = {}
    try:
        resp = requests.get(NCAA_SCOREBOARD_URL, timeout=10)
        resp.raise_for_status()
        ncaa_data = resp.json()
        ncaa_events = ncaa_data.get("events", [])
    except requests.RequestException as e:
        print("Could not fetch NCAA scoreboard:", e)
        ncaa_events = []

    live_keys = get_live_game_keys(nba_events, "nba") | get_live_game_keys(ncaa_events, "ncaa")
    alerted_games &= live_keys

    nba_close = process_league({"events": nba_events}, "nba", is_college=False)
    ncaa_close = process_league(ncaa_data if ncaa_data else {"events": ncaa_events}, "ncaa", is_college=True)
    return nba_events, ncaa_events, nba_close, ncaa_close


def main():
    once = "--once" in sys.argv or "-o" in sys.argv
    if once:
        load_alerted_games()
        run_one_check()
        save_alerted_games()
        return

    print("Close game detector started (NBA + NCAA). Checking every", CHECK_INTERVAL, "seconds...")
    while True:
        nba_events, ncaa_events, nba_close, ncaa_close = run_one_check()
        if nba_close == 0 and ncaa_close == 0:
            if nba_events or ncaa_events:
                print("Checked", len(nba_events), "NBA,", len(ncaa_events), "NCAA — no close games right now.")
            else:
                print("No games on the scoreboard.")
        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
