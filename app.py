import os
import psycopg
from psycopg.rows import dict_row
from flask import Flask, jsonify, request
from psycopg_pool import ConnectionPool

app = Flask(__name__)

DB_CONFIG = {
    "host": os.environ["DB_HOST"],
    "user": os.environ["DB_USER"],
    "password": os.environ["DB_PASSWORD"],
    "dbname": os.environ["DB_NAME"],
}

pool = ConnectionPool(
    kwargs={**DB_CONFIG, "row_factory": dict_row},
    min_size=1,
    max_size=5,
    open=True,
)

def init_db():
    with pool.connection() as conn:
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
    with pool.connection() as conn:
        rows = conn.execute("SELECT id, text FROM notes ORDER BY id").fetchall()
    return jsonify(rows)

@app.route("/notes", methods=["POST"])
def add_note():
    data = request.get_json()
    with pool.connection() as conn:
        note = conn.execute(
            "INSERT INTO notes (text) VALUES (%s) RETURNING id, text",
            (data["text"],),
        ).fetchone()
    return jsonify(note), 201

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)