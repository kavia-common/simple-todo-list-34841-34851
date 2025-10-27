# Integration Guide: todo_frontend + todo_database

This guide explains how to run the Flask API server and the React frontend together, how ports and CORS are configured, how to switch ports if one is busy, and how to quickly verify add/view/delete functionality.

## Components and locations
- Backend API (Flask + SQLite): simple-todo-list-34841-34851/todo_database
- Frontend UI (React): simple-todo-list-34841-34850/todo_frontend

## Defaults
- API host/port: 0.0.0.0:5001
- CORS allowed origin: http://localhost:3000
- Frontend dev server: http://localhost:3000
- Frontend API base URL: http://localhost:5001

## 1) Start the Flask API server
From the todo_database directory:
1. Ensure Python 3 is available.
2. Start the server:
   python3 api_server.py

Expected:
- Binds to 0.0.0.0:5001
- CORS enabled for http://localhost:3000
- SQLite DB file: myapp.db (auto creates/ensures schema)

Environment overrides:
- To change port (e.g., to 5002 if 5001 is in use):
  PORT=5002 python3 api_server.py

- To change DB file:
  SQLITE_DB=/path/to/custom.db python3 api_server.py

Health checks:
- List todos: curl http://localhost:5001/todos
- When using port 5002: curl http://localhost:5002/todos

## 2) Start the React frontend
From the todo_frontend directory:
1. Install dependencies (first run only):
   npm install
2. Start the dev server:
   npm start

Open http://localhost:3000 in your browser.

API base URL in the frontend:
- Default is http://localhost:5001 (defined in src/App.js as API_BASE)

If you changed the API port to 5002:
- Option A (quick edit): Update API_BASE in simple-todo-list-34841-34850/todo_frontend/src/App.js
  const API_BASE = 'http://localhost:5002';
  Then restart npm start if already running.
- Option B (optional improvement): Introduce an environment variable (e.g., REACT_APP_API_BASE) and use it in code. Not implemented by default.

## 3) Port-in-use fallback
- If port 5001 is already in use, start the API on 5002:
  PORT=5002 python3 api_server.py
- Then update the frontend API base URL to http://localhost:5002 as noted above.

## 4) Quick verification checklist
With the API running and frontend open at http://localhost:3000:

- View:
  - Load page; you should see "Your Tasks" and either existing tasks or "No tasks yet. Add your first one!".

- Add:
  - Type "Buy milk" into the input and click "Add".
  - "Buy milk" should appear at the top of the list without a full page reload.

- Refresh:
  - Click "Refresh". The list should reload and still show "Buy milk".

- Delete:
  - Click "Delete" next to "Buy milk".
  - The item should disappear from the list.

- Error handling (optional):
  - Stop the API server and click "Refresh" in the UI.
  - You should see an error banner indicating fetch failed.

Endpoints used by the frontend:
- GET /todos
- POST /todos  (body: { "text": "..." })
- DELETE /todos/:id

Notes:
- API CORS is configured to allow http://localhost:3000.
- The API binds to 0.0.0.0 so it is accessible from localhost and other interfaces on the machine.
