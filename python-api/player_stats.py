import requests
from collections import defaultdict
import re

def get_ratings(data: dict, period: str):
    """
    Args:
        data (dict): player stats
        period (str): last/best
        
    Returns:
        dict : ratings for a specific period last/best
    """
    rapid_rating = data.get("chess_rapid", {}).get(f"{period}", {}).get("rating", "N/A")
    blitz_rating = data.get("chess_blitz", {}).get(f"{period}", {}).get("rating", "N/A")
    bullet_rating = data.get("chess_bullet", {}).get(f"{period}", {}).get("rating", "N/A")
    
    return {
        f"{period}_rapid_rating": rapid_rating,
        f"{period}_blitz_rating": blitz_rating,
        f"{period}_bullet_rating": bullet_rating
    }

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
    
    response = requests.get(player_elo_stats, headers=headers)
    
    if response.status_code != 200:
        return {"error": f"Player {username} not found or access forbidden", "status_code": response.status_code}

    data = response.json()
    last_stats = get_ratings(data, "last")
    best_stats = get_ratings(data, "best")
    
    return {
        1: last_stats,
        2: best_stats
    }

print(get_player_stats("mateispaimata"))