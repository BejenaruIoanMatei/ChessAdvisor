from utils.deps import requests, HTTPException, defaultdict, re

def compute_top_10(openings_dict: dict, key: str):
    openings_wr = []
    for opening_name, stats in openings_dict.items():
        total = stats["wins"] + stats["losses"] + stats["draws"]
        if total >= 10: 
            win_rate = (stats["wins"] / total) * 100
            openings_wr.append({
                "opening": opening_name,
                "wr": win_rate,
                "wins": stats["wins"],
                "losses": stats["losses"],
                "draws": stats["draws"],
                "total": total
            })

    openings_wr.sort(key=lambda x: x[key], reverse = True)
    return openings_wr[:10]

def player_games(username: str):
    archives_url = f"https://api.chess.com/pub/player/{username}/games/archives"

    headers = {
        "User-Agent": "ChessAdvisorApp/1.0"
    }

    try:
        response = requests.get(archives_url, headers=headers)
        response.raise_for_status()
        archives = response.json()["archives"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading archives: {e}")

    openings_white = defaultdict(lambda: {"wins": 0, "losses": 0, "draws": 0})
    openings_black = defaultdict(lambda: {"wins": 0, "losses": 0, "draws": 0})

    match_results = {
        "wins": ["win"],
        "losses": ["loss", "abandoned", "timeout", "checkmated", "resigned"],
        "draws": ["agreed", "stalemate", "draw", "repetition"],
    }

    for archive_url in archives:
        try:
            response = requests.get(archive_url, headers=headers)
            response.raise_for_status()
            games = response.json()["games"]
        except Exception:
            continue

        for game in games:
            pgn = game.get("pgn", "")
            opening_match = re.search(
                r'\[ECOUrl "https://www\.chess\.com/openings/(.+?)"\]', pgn
            )
            if not opening_match:
                continue

            opening_name = opening_match.group(1).replace("-", " ")

            is_white = game["white"]["username"].lower() == username
            is_black = game["black"]["username"].lower() == username

            if not (is_white or is_black):
                continue

            result = game["white"]["result"] if is_white else game["black"]["result"]
            target_dict = openings_white if is_white else openings_black

            if result in match_results["wins"]:
                target_dict[opening_name]["wins"] += 1
            elif result in match_results["losses"]:
                target_dict[opening_name]["losses"] += 1
            elif result in match_results["draws"]:
                target_dict[opening_name]["draws"] += 1

    return openings_white, openings_black