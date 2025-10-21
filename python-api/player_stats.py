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
    
def get_stats_for_time_management_all(data: dict):
    """wins, draws, losses
    
    Args:
        data (dict): player stats

    Returns:
        dict: W-D-L for rapid/blitz/bullet
    """
    rapid_rating = data.get("chess_rapid", {}).get("record", {})
    blitz_rating = data.get("chess_blitz", {}).get("record", {})
    bullet_rating = data.get("chess_bullet", {}).get("record", {})
    
    return {
        'stats_rapid': rapid_rating,
        'stats_blitz': blitz_rating,
        'stats_bullet': bullet_rating,
    }
    
def get_stats_for_time_management_only(data: dict, time_control: str):
    """wins, draws, losses for rapid/blitz/bullet

    Args:
        data (dict): player stats
        time_control (str): rapid/blitz/bullet

    Returns:
        dict: wins, draws, losses for rapid/blitz/bullet
    """
    stats = data.get(f"chess_{time_control}", {}).get("record", {})
    
    return {
        f"stats_{time_control}": stats
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
    
    player_stats = {
        'player_ratings_last': get_ratings(data, 'last'),
        'player_ratings_best': get_ratings(data, 'best'),
        'stats_for_time_management_all': get_stats_for_time_management_all(data),
        'stats_for_rapid': get_stats_for_time_management_only(data, 'rapid'),
        'stats_for_blitz': get_stats_for_time_management_only(data, 'blitz'),
        'stats_for_bullet': get_stats_for_time_management_only(data, 'bullet')
    }
    
    return player_stats

print(get_player_stats("bogdogun"))
