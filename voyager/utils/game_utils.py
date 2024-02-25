import requests


def get_game_initial_data(dungeon_map):
    response = requests.post(f"http://localhost:8000/game/data", json={"dungeon": dungeon_map})
    return response.json()
