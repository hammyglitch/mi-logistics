import os
from flask import Flask, render_template, request, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)

# On Render, use /tmp for writable storage (free tier has ephemeral filesystem)
# Locally, use the app directory
if os.environ.get('RENDER'):
    DB_PATH = '/tmp/logos.db'
else:
    DB_PATH = os.path.join(os.path.dirname(__file__), 'logos.db')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS responses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT NOT NULL, logo_name TEXT NOT NULL,
        response TEXT NOT NULL, timestamp TEXT NOT NULL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS stars (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT NOT NULL UNIQUE, logo_name TEXT NOT NULL,
        timestamp TEXT NOT NULL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        playlist_rating INTEGER,
        colour_changes TEXT,
        further_requests TEXT,
        timestamp TEXT NOT NULL)''')
    conn.commit(); conn.close()

def query_db(sql, args=()):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor(); c.execute(sql, args)
    rv = c.fetchall(); conn.close()
    return [dict(r) for r in rv]

@app.route('/')
def home(): return render_template('index.html')

@app.route('/logos')
def logos(): return render_template('logos.html')

@app.route('/all-logos')
def all_logos(): return render_template('all_logos.html')

@app.route('/results')
def results(): return render_template('results.html')

@app.route('/admin')
def admin(): return render_template('admin.html')

@app.route('/vote', methods=['POST'])
def vote():
    data = request.get_json(force=True)
    cat, logo, resp = data.get('category','').strip(), data.get('logo','').strip(), data.get('response','').strip()
    if not logo or not cat or resp not in ('like','dislike'):
        return jsonify({'status':'error'}), 400
    conn = sqlite3.connect(DB_PATH); c = conn.cursor()
    c.execute('INSERT INTO responses (category,logo_name,response,timestamp) VALUES (?,?,?,?)',
              (cat, logo, resp, datetime.now().isoformat()))
    conn.commit(); conn.close()
    return jsonify({'status':'ok'})

@app.route('/star', methods=['POST'])
def star():
    data = request.get_json(force=True)
    cat, logo, action = data.get('category','').strip(), data.get('logo','').strip(), data.get('action','set')
    if not cat: return jsonify({'status':'error'}), 400
    conn = sqlite3.connect(DB_PATH); c = conn.cursor()
    if action == 'clear':
        c.execute('DELETE FROM stars WHERE category=?', (cat,))
    else:
        c.execute('''INSERT INTO stars (category,logo_name,timestamp) VALUES (?,?,?)
                     ON CONFLICT(category) DO UPDATE SET logo_name=excluded.logo_name,timestamp=excluded.timestamp''',
                  (cat, logo, datetime.now().isoformat()))
    conn.commit(); conn.close()
    return jsonify({'status':'ok'})

@app.route('/feedback', methods=['POST'])
def feedback():
    data = request.get_json(force=True)
    rating   = data.get('playlist_rating', 0)
    colours  = data.get('colour_changes', '').strip()
    requests = data.get('further_requests', '').strip()
    conn = sqlite3.connect(DB_PATH); c = conn.cursor()
    c.execute('INSERT INTO feedback (playlist_rating,colour_changes,further_requests,timestamp) VALUES (?,?,?,?)',
              (rating, colours, requests, datetime.now().isoformat()))
    conn.commit(); conn.close()
    return jsonify({'status':'ok'})

@app.route('/api/admin-data')
def admin_data():
    votes    = query_db('SELECT * FROM responses ORDER BY timestamp DESC')
    stars    = query_db('SELECT * FROM stars ORDER BY timestamp DESC')
    feedback = query_db('SELECT * FROM feedback ORDER BY timestamp DESC')
    return jsonify({'votes': votes, 'stars': stars, 'feedback': feedback})

@app.route('/api/results')
def api_results():
    rows = query_db('''SELECT category,logo_name,
        SUM(CASE WHEN response="like" THEN 1 ELSE 0 END) AS likes,
        SUM(CASE WHEN response="dislike" THEN 1 ELSE 0 END) AS dislikes,
        COUNT(*) AS total
        FROM responses GROUP BY category,logo_name ORDER BY category,likes DESC''')
    stars = query_db('SELECT category,logo_name FROM stars')
    fb    = query_db('SELECT * FROM feedback ORDER BY id DESC LIMIT 1')
    grouped = {}
    for r in rows:
        grouped.setdefault(r['category'],[]).append(r)
    return jsonify({'votes':grouped, 'stars':{s['category']:s['logo_name'] for s in stars}, 'feedback':fb[0] if fb else None})

@app.route('/api/reset', methods=['POST'])
def reset():
    conn = sqlite3.connect(DB_PATH)
    conn.execute('DELETE FROM responses')
    conn.execute('DELETE FROM stars')
    conn.execute('DELETE FROM feedback')
    conn.commit(); conn.close()
    return jsonify({'status':'ok'})

init_db()

if __name__ == '__main__':
    print("\n  MI LOGISTICS")
    print("  http://localhost:5000")
    print("  http://localhost:5000/admin\n")
    app.run(debug=False, host='0.0.0.0', port=5000)
