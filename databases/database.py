import sqlite3

DB_PATH = "database.sqlite"

def save_participant(data: dict):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS participants (
            username TEXT PRIMARY KEY,
            name TEXT,
            age TEXT,
            date TEXT,
            faculty TEXT,
            hobby TEXT,
            city TEXT,
            metro TEXT,
            fact TEXT,
            phrase TEXT
        )
    """)

    cur.execute("""
        INSERT INTO participants(username, name, age, date, faculty, hobby, city, metro, fact, phrase)
        VALUES (:username, :name, :age, :date, :faculty, :hobby, :city, :metro, :fact, :phrase)
    """, {
        "username": data.get("username", ""),
        "name": data.get("name", ""),
        "age": data.get("age", ""),
        "date": data.get("date", ""),
        "faculty": data.get("faculty", ""),
        "hobby": data.get("hobby", ""),
        "city": data.get("city", ""),
        "metro": data.get("metro", ""),
        "fact": data.get("fact", ""),
        "phrase": data.get("phrase", "")
    })

    con.commit()
    con.close()

def participant_exists(username: str) -> bool:
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("SELECT 1 FROM participants WHERE username = ?", (username,))
    exists = cur.fetchone() is not None
    con.close()
    return exists

def usernames():
    con = sqlite3.connect('databases/users.sqlite')
    cur = con.cursor()
    query = ('SELECT telega FROM participants')
    usernames = cur.execute(query).fetchall()
    return usernames

def get_participant(username):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("""
        SELECT username, name, age, date, faculty, hobby, city, metro, fact, phrase
        FROM participants
        WHERE username = ?
    """, (username,))
    userdata = cur.fetchone()
    con.close()
    return userdata

def get_usernames():
    con = sqlite3.connect('database.sqlite')
    cur = con.cursor()
    query = ('SELECT username FROM participants')
    usernames = cur.execute(query).fetchall()
    return usernames
