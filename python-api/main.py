import requests
from collections import defaultdict
from fastapi import FastAPI
import re
from utils import player_stats
from fastapi import HTTPException


app = FastAPI()

@app.get("player/{username}/profile")
def get_player_profile(username: str):
    """
    Get player profile including username, chess.com url, avatar, country

    Args:
        username (str): player username on chess.com
    """
    username = username.lower()
    player_profile = f"https://api.chess.com/pub/player/{username}"
    
    headers = {
        "User-Agent": "ChessAdvisorApp/1.0"
    }
    try:
        response = requests.get(player_profile, headers = headers)
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code = 503, 
            detail = f"connection error {str(e)}"
        )
    
    if response.status_code != 200:
        raise  HTTPException(
            status_code = response.status_code,
            detail = f"chess.com returned {response.status_code}"
        )
    
    try:
        data = response.json()
    except ValueError:
        raise HTTPException(status_code = 502, detail = "invalid response from server")
    
    return data
    

@app.get("/player/{username}/stats")
def get_player_stats(username: str):
    """
    Args:
        username (str): player username

    Returns:
        dict : player combined stats
    """
    username = username.lower()
    player_elo_stats = f"https://api.chess.com/pub/player/{username}/stats"
    
    headers = {
        "User-Agent": "ChessAdvisorApp/1.0"
    }
    
    try: 
        response = requests.get(player_elo_stats, headers=headers)
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code = 503,
            detail = f"connection error {str(e)}"
        )
    
    if response.status_code != 200:
        raise HTTPException(
            status_code = response.status_code,
            detail = f"chess.com returned {response.status.code}"
        )

    try:
        data = response.json()
    except ValueError:
        raise HTTPException(
            status_code = 502,
            detail = "invalid response from server"
        )
    
    player_data = {
        'player_ratings_last': player_stats.get_ratings(data, 'last'),
        'player_ratings_best': player_stats.get_ratings(data, 'best'),
        'stats_for_rapid': player_stats.get_stats_for_time_management_only(data, 'rapid'),
        'stats_for_blitz': player_stats.get_stats_for_time_management_only(data, 'blitz'),
        'stats_for_bullet': player_stats.get_stats_for_time_management_only(data, 'bullet')
    }

    return player_data

@app.get("/player/{username}/worst")
def worst_openings_wr(username: str):
    """
        Searches the player, finds his archives where the games are stored.
        Foreach game, the wins, losses, draws are stored.
        In addition to match results, this function gets the openings and for every opening
    with more than 10 games it displays the win rate (W - L - D)
    
        Top 10 worst openings for a player regarding the win rate
    Args:
        username (str): player username
    """
    username = username.lower()
    archives_url = f"https://api.chess.com/pub/player/{username}/games/archives"
    
    headers = {
        'User-Agent': 'ChessAdvisorApp/1.0'
    }
    
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
    
    top_10_worst = openings_with_wr[:10]

    return {
        "player": username,
        "total_openings_analyzed": len(openings_with_wr),
        "worst_openings": top_10_worst
    }

    
