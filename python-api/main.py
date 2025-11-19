from fastapi import FastAPI
from utils.deps import requests, HTTPException
from utils.player_games import player_games, compute_top_10
from utils.player_stats import *

app = FastAPI()

@app.get("/player/{username}/profile")
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
        'player_ratings_last': get_ratings(data, 'last'),
        'player_ratings_best': get_ratings(data, 'best'),
        'stats_for_rapid': get_stats_for_time_management_only(data, 'rapid'),
        'stats_for_blitz': get_stats_for_time_management_only(data, 'blitz'),
        'stats_for_bullet': get_stats_for_time_management_only(data, 'bullet')
    }

    return player_data

@app.get("/player/{username}/player_most_played_openings")
def most_played_op(username: str):
    username = username.lower()
    openings_white, openings_black = player_games(username)

    return {
        "player": username,
        "white": compute_top_10(openings_white, "total"),
        "black": compute_top_10(openings_black, "total"),
    }

@app.get('/player/{username}/player_best_openings')
def best_played_op(username: str):
    username = username.lower()
    openings_white, openings_black = player_games(username)
    
    return {
        "player": username,
        "white": compute_top_10(openings_white, "wr"),
        "black": compute_top_10(openings_black, "wr"),
    }


    
