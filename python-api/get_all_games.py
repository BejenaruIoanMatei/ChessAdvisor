import requests
from collections import defaultdict
import re

def worst_openings(username: str):
    username = username.lower()
    archives_url = f"https://api.chess.com/pub/player/{username}/games/archives"
    headers = {'User-Agent': 'ChessAdvisorApp/1.0'}
    
    try:
        response = requests.get(archives_url, headers=headers)
        response.raise_for_status()
        archives = response.json()["archives"]
    except Exception as e:
        print(f"Error to archvies: {e}")
        return
    
    openings_stats = defaultdict(lambda: {"wins": 0, "losses": 0, "draws": 0})
    
    for archive_url in archives:
        try:
            response = requests.get(archive_url, headers=headers)
            response.raise_for_status()
            games = response.json()["games"]
            
            for game in games:
                pgn = game.get("pgn", "")
                opening_match = re.search(r'\[ECOUrl "https://www\.chess\.com/openings/(.+?)"\]', pgn)
                
                if not opening_match:
                    continue
                
                opening_name = opening_match.group(1).replace("-", " ")
                
                if game["white"]["username"].lower() == username:
                    player_result = game["white"]["result"]
                elif game["black"]["username"].lower() == username:
                    player_result = game["black"]["result"]
                else:
                    continue
                
                if player_result == "win":
                    openings_stats[opening_name]["wins"] += 1
                elif player_result == "loss":
                    openings_stats[opening_name]["losses"] += 1
                elif player_result == "abandoned":
                    openings_stats[opening_name]["losses"] += 1
                elif player_result == "stalemate":
                    openings_stats[opening_name]["draws"] += 1
                elif player_result == "draw":
                    openings_stats[opening_name]["draws"] += 1
                elif player_result == "timeout":
                    openings_stats[opening_name]["losses"] += 1
                elif player_result == "checkmated":
                    openings_stats[opening_name]["losses"] += 1
                
                    
        except Exception as e:
            print(f"Error to archive: {e}")
            continue
    
    if not openings_stats:
        print(f"No games found for opening {username}")
        return
    
    total_games = sum(s["wins"] + s["losses"] + s["draws"] for s in openings_stats.values())
    print(f"Total games: {total_games}")
    print(f"Total different openings: {len(openings_stats)}\n")
    
    openings_with_wr = []
    for opening_name, stats in openings_stats.items():
        total = stats["wins"] + stats["losses"] + stats["draws"]
        if total >= 10:
            win_rate = (stats["wins"] / total) * 100
            openings_with_wr.append({
                "opening": opening_name,
                "wr": win_rate,
                "wins": stats["wins"],
                "losses": stats["losses"],
                "draws": stats["draws"],
                "total": total
            })
    
    openings_with_wr.sort(key=lambda x: x["wr"])
    
    print(f"\nTop 10 worst openings for {username}:\n")
    for i, opening in enumerate(openings_with_wr[:10], 1):
        print(f"{i}. {opening['opening']}")
        print(f"   Win Rate: {opening['wr']:.2f}%")
        print(f"   Record: {opening['wins']}W - {opening['losses']}L - {opening['draws']}D ({opening['total']} jocuri)")
        print()

worst_openings("damipace")