import requests

BASE_URL = 'http://127.0.0.1:8000'

def move(action):
    url = f"{BASE_URL}/game/move"
    data = {"action": action}
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, json=data, headers=headers)
    return response.json()

result = move("W")

print(result)
