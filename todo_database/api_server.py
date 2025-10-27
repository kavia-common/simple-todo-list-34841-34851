#!/usr/bin/env python3
"""
Minimal Flask API server for the todo_database.

Exposes:
- GET /todos: Retrieve all todos
- POST /todos: Create a new todo (JSON body: { "text": "Task text" })
- DELETE /todos/<id>: Delete a todo by ID

CORS is enabled for http://localhost:3000

Server binds to 0.0.0.0:5001
- If port 5001 is in use, set PORT=5002 (or any open port) before running:
  PORT=5002 python3 api_server.py

Frontend default API base URL is http://localhost:5001 (see todo_frontend/src/App.js).
If you change the API port, update the frontend API base accordingly.
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import os
from typing import Dict, Any, List, Optional

DB_NAME = os.environ.get("SQLITE_DB", "myapp.db")

app = Flask(__name__)
# Enable CORS for the frontend origin
CORS(app, resources={r"/*": {"origins": ["http://localhost:3000"]}})


def dict_row_factory(cursor, row):
    """sqlite3 row factory to return dict-like rows."""
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def get_connection():
    """Get a SQLite connection with row_factory set."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = dict_row_factory
    # Enable foreign keys just in case
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def ensure_schema():
    """
    Ensure the 'todos' table exists.
    """
    conn = sqlite3.connect(DB_NAME)
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS todos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
    finally:
        conn.close()


# PUBLIC_INTERFACE
@app.get("/todos")
def list_todos():
    """
    Get all todo items.

    Returns:
        200 OK with JSON array of todos:
        [
          { "id": 1, "text": "Task", "created_at": "2025-01-01 12:00:00" },
          ...
        ]
    """
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, text, created_at FROM todos ORDER BY id DESC")
        items = cur.fetchall()
        return jsonify(items), 200
    except sqlite3.Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        try:
            conn.close()
        except Exception:
            pass


# PUBLIC_INTERFACE
@app.post("/todos")
def create_todo():
    """
    Create a new todo.

    Request JSON:
        { "text": "Task text" }

    Returns:
        201 Created with created todo JSON
        400 Bad Request if input invalid
    """
    if not request.is_json:
        return jsonify({"error": "Expected application/json"}), 400

    data: Dict[str, Any] = request.get_json(silent=True) or {}
    text: Optional[str] = data.get("text")
    if text is None:
        return jsonify({"error": "Field 'text' is required"}), 400
    if not isinstance(text, str):
        return jsonify({"error": "Field 'text' must be a string"}), 400
    text = text.strip()
    if not text:
        return jsonify({"error": "Field 'text' cannot be empty"}), 400
    if len(text) > 500:
        return jsonify({"error": "Field 'text' is too long (max 500 chars)"}), 400

    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO todos (text) VALUES (?)", (text,))
        conn.commit()
        todo_id = cur.lastrowid
        cur.execute("SELECT id, text, created_at FROM todos WHERE id = ?", (todo_id,))
        created = cur.fetchone()
        return jsonify(created), 201
    except sqlite3.Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        try:
            conn.close()
        except Exception:
            pass


# PUBLIC_INTERFACE
@app.delete("/todos/<int:todo_id>")
def delete_todo(todo_id: int):
    """
    Delete a todo by ID.

    Path params:
        todo_id: integer ID of the todo to delete

    Returns:
        200 OK with { "deleted": true, "id": <id> } when deleted
        404 Not Found if the todo does not exist
    """
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
        conn.commit()
        if cur.rowcount == 0:
            return jsonify({"error": "Todo not found"}), 404
        return jsonify({"deleted": True, "id": todo_id}), 200
    except sqlite3.Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        try:
            conn.close()
        except Exception:
            pass


def main():
    """Entrypoint to start the API server."""
    # Ensure schema is present before serving traffic
    ensure_schema()
    host = "0.0.0.0"
    port = int(os.environ.get("PORT", 5001))
    # Use threaded=True to allow simple concurrent requests in dev
    app.run(host=host, port=port, debug=False, threaded=True)


if __name__ == "__main__":
    main()
