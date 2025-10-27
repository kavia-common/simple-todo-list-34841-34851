#!/usr/bin/env python3
"""Test SQLite database connection and schema presence"""

import sqlite3
import sys
import os

DB_NAME = "myapp.db"

try:
    # Check if database file exists
    if not os.path.exists(DB_NAME):
        print(f"Database file '{DB_NAME}' not found")
        sys.exit(1)
    
    # Connect to database and get version
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT sqlite_version()")
    version = cursor.fetchone()[0]

    # Verify todos table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='todos'")
    row = cursor.fetchone()
    has_todos = row is not None

    conn.close()
    
    print(f"SQLite version: {version}")
    print(f"Todos table present: {has_todos}")
    sys.exit(0 if has_todos else 2)
    
except sqlite3.Error as e:
    print(f"Connection failed: {e}")
    sys.exit(1)
