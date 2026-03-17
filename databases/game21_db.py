import json
import os

DB_FILE = 'databases/active_games.json'

def load_games():
    with open(DB_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_game(message_id, data):
    games = load_games()
    games[str(message_id)] = data 
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(games, f, ensure_ascii=False, indent=4)