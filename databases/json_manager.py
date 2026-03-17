import json
from pathlib import Path

ACTIONS_FILE = Path("databases/actions.json")
USERS_FILE = Path("databases/users.json")

def load_actions():
    with open(ACTIONS_FILE, "r", encoding="utf-8") as file:
        return json.load(file)

def load_users():
    with open(USERS_FILE, "r", encoding="utf-8") as file:
        return json.load(file)

def save_user(user_id: int, username: str):
    users = load_users()
    users[str(user_id)] = username
    with open(USERS_FILE, "w", encoding="utf-8") as file:
        json.dump(users, file, ensure_ascii=False, indent=4)