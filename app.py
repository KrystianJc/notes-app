import os
import psycopg
from psycopg.rows import dict_row
from flask import Flask, jsonify, request

app = Flask(__name__)

DB_CONFIG = {
    "host": os.environ["DB_HOST"],
    "user": os.environ["DB_USER"],
    "password": os.environ["DB_PASSWORD"],
    "dbname": os.environ["DB_NAME"],
}

def get_connection():
    return psycopg.connect(**DB_CONFIG, row_factory=dict_row)

def init_db():
    with get_connection() as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS notes ("
            "id SERIAL PRIMARY KEY, "
            "text TEXT NOT NULL)"
        )

@app.route("/health")
def health():
    return jsonify(status="ok")

@app.route("/notes", methods=["GET"])
def list_notes():
    with get_connection() as conn:
        rows = conn.execute("SELECT id, text FROM notes ORDER BY id").fetchall()
    return jsonify(rows)

@app.route("/notes", methods=["POST"])
def add_note():
    data = request.get_json()
    with get_connection() as conn:
        note = conn.execute(
            "INSERT INTO notes (text) VALUES (%s) RETURNING id, text",
            (data["text"],),
        ).fetchone()
    return jsonify(note), 201

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)