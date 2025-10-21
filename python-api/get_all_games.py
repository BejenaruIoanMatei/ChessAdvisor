import requests
from collections import defaultdict
import re

def worst_openings_wr(username: str):
    """_summary_
        Searches the player, finds his archives where the games are stored.
        Foreach game, the wins, losses, draws are stored.
        In addition to match results, this function gets the openings and for every opening
    with more than 10 games it displays the win rate (W - L - D)
    
        Top 10 worst openings for a player regarding the win rate
    Args:
        username (str): _description_
    """
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
            
            match_results = {
                'wins': ['win'],
                'losses': ['loss', 'abandoned', 'timeout', 'checkmated', 'resigned'],
                'draws': ['agreed','stalemate', 'draw', 'repetition'],
            }
            
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
                
                if player_result in match_results["wins"]:
                    openings_stats[opening_name]["wins"] += 1
                elif player_result in match_results["losses"]:
                    openings_stats[opening_name]["losses"] += 1
                elif player_result in match_results["draws"]:
                    openings_stats[opening_name]["draws"] += 1                
                    
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
    for i, opening in enumerate(openings_with_wr, 1):
        print(f"{i}. {opening['opening']}")
        print(f"   Win Rate: {opening['wr']:.2f}%")
        print(f"   Record: {opening['wins']}W - {opening['losses']}L - {opening['draws']}D ({opening['total']} jocuri)")
        print()

worst_openings_wr("damipace")