import requests
from fastapi import FastAPI

app = FastAPI()

@app.get("/player/{username}")
def get_player_stats(username: str):
    username = username.lower()
    url = f"https://api.chess.com/pub/player/{username}/stats"

    headers = {
        "User-Agent": "MyChessApp/1.0 (https://yourwebsite.com)"
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return {"error": f"Player {username} not found or access forbidden", "status_code": response.status_code}

    data = response.json()
    blitz_rating = data.get("chess_blitz", {}).get("last", {}).get("rating", "N/A")
    rapid_rating = data.get("chess_rapid", {}).get("last", {}).get("rating", "N/A")
    bullet_data = data.get("chess_bullet", {}).get("last", {}).get("rating", "N/A")
    
    return data
        # "username": username,
        # "chess_blitz": blitz_rating,
        # "chess_rapid": rapid_rating,
        # "chess_bullet": bullet_data

    
