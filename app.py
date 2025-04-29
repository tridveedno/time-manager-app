from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import sqlite3
import json

app = Flask(__name__)
CORS(app)

# --- DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    # Allocations
    c.execute('''
        CREATE TABLE IF NOT EXISTS allocations (
            id TEXT PRIMARY KEY,
            project_id INTEGER,
            member_id TEXT,
            hours INTEGER,
            week_start TEXT
        )
    ''')

    # Projects
    c.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY,
            name TEXT,
            hours INTEGER,
            hours_type TEXT,
            hours_input INTEGER,
            color TEXT,
            start_date TEXT,
            end_date TEXT,
            status TEXT
        )
    ''')

    # Members
    c.execute('''
        CREATE TABLE IF NOT EXISTS members (
            id TEXT PRIMARY KEY,
            name TEXT,
            weekly_capacity INTEGER
        )
    ''')

    # Scenarios
    c.execute('''
        CREATE TABLE IF NOT EXISTS scenarios (
            id TEXT PRIMARY KEY,
            name TEXT,
            data TEXT
        )
    ''')

    conn.commit()
    conn.close()

init_db()

# --- ROUTES ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/save', methods=['POST'])
def save_allocation():
    data = request.get_json()
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    for alloc in data:
        c.execute('''
            INSERT OR REPLACE INTO allocations (id, project_id, member_id, hours, week_start)
            VALUES (?, ?, ?, ?, ?)
        ''', (alloc['id'], alloc['projectId'], alloc['memberId'], alloc['hours'], alloc['weekStart']))
    conn.commit()
    conn.close()
    return jsonify({"message": "Saved successfully"}), 200

@app.route('/load', methods=['GET'])
def load_allocations():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT id, project_id, member_id, hours, week_start FROM allocations')
    rows = c.fetchall()
    conn.close()
    data = []
    for row in rows:
        data.append({
            "id": row[0],
            "projectId": row[1],
            "memberId": row[2],
            "hours": row[3],
            "weekStart": row[4]
        })
    return jsonify(data)

@app.route('/save-all', methods=['POST'])
def save_all():
    data = request.get_json()

    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    # Optional: clear existing data to replace it
    c.execute('DELETE FROM projects')
    c.execute('DELETE FROM members')
    c.execute('DELETE FROM allocations')
    c.execute('DELETE FROM scenarios')

    for p in data.get('projects', []):
        c.execute('''INSERT INTO projects VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (p['id'], p['name'], p['hours'], p['hoursType'], p.get('hoursInput'),
                   p['color'], p['startDate'], p['endDate'], p['status']))

    for m in data.get('members', []):
        c.execute('''INSERT INTO members VALUES (?, ?, ?)''',
                  (m['id'], m['name'], m['weeklyCapacity']))

    for a in data.get('allocations', []):
        c.execute('''INSERT OR REPLACE INTO allocations VALUES (?, ?, ?, ?, ?)''',
                  (a['id'], a['projectId'], a['memberId'], a['hours'], a['weekStart']))

    for s in data.get('scenarios', []):
        c.execute('''INSERT INTO scenarios VALUES (?, ?, ?)''',
                  (s['id'], s['name'], json.dumps(s)))

    conn.commit()
    conn.close()
    return jsonify({"message": "All data saved"}), 200

@app.route('/load-all', methods=['GET'])
def load_all():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute('SELECT * FROM projects')
    projects = [dict(zip([d[0] for d in c.description], row)) for row in c.fetchall()]

    c.execute('SELECT * FROM members')
    members = [dict(zip([d[0] for d in c.description], row)) for row in c.fetchall()]

    c.execute('SELECT * FROM allocations')
    allocations = [dict(zip([d[0] for d in c.description], row)) for row in c.fetchall()]

    c.execute('SELECT * FROM scenarios')
    scenarios = [json.loads(row[2]) for row in c.fetchall()]

    conn.close()

    return jsonify({
        'projects': projects,
        'members': members,
        'allocations': allocations,
        'scenarios': scenarios
    })

if __name__ == '__main__':
    app.run(debug=True)
