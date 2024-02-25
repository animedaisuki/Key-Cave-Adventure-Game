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
    game_app = GameApp()
    dungeon_name = request.json.get('dungeon')
    game_app.load_game(dungeon_name)
    return jsonify({'message': 'Game started'}), 200

@app.route('/game/data', methods=['POST'])
def get_game_data():
    game_data = GameApp()
    dungeon_name = request.json.get('dungeon')
    game_data.load_game(dungeon_name)
    status = game_data.get_game_state()
    return Response(json.dumps(status, indent=None), mimetype='application/json'), 200

@app.route('/game/move', methods=['POST'])
def move_player():
    if game_app.get_game_logic().won():
        return jsonify({'message': 'You have won the game'}), 200
    if game_app.get_game_logic().check_game_over():
        return jsonify({'message': 'You have lost the game'}), 200
    action = request.json.get('action')
    if action not in VALID_ACTIONS:
        return jsonify({'error': 'Invalid action'}), 400
    message = game_app.process_action(action)
    return jsonify({'message': message}), 200

@app.route('/game/status', methods=['GET'])
def get_status():
    status = game_app.get_game_state()
    return Response(json.dumps(status, indent=None), mimetype='application/json'), 200

if __name__ == '__main__':
    app.run(port=8000, debug=True)
