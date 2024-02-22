# app.py
from flask import Flask, request, jsonify, Response
import json
from flask_cors import CORS

from game import GameApp
from game_view import *

app = Flask(__name__)

game_app = GameApp()
CORS(app)

@app.route('/game/start', methods=['POST'])
def start_game():
    global game_app
    game_app = GameApp()  # 重置游戏状态
    return jsonify({'message': 'Game started'}), 200

@app.route('/game/move', methods=['POST'])
def move_player():
    action = request.json.get('action')
    if action not in VALID_ACTIONS:
        return jsonify({'error': 'Invalid action'}), 400
    message = game_app.process_action(action)
    return jsonify({'message': message}), 200

@app.route('/game/status', methods=['GET'])
def get_status():
    status = game_app.get_game_state()
    return Response(json.dumps(status, indent=None), mimetype='application/json')

if __name__ == '__main__':
    app.run(port=8000, debug=True)
