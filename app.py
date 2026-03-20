import os
from flask import Flask, render_template, request, jsonify
from datetime import datetime

app = Flask(__name__)

# ── DATABASE SETUP ──
# Uses PostgreSQL on Render (DATABASE_URL set automatically)
# Falls back to SQLite locally
DATABASE_URL = os.environ.get('DATABASE_URL')

if DATABASE_URL:
    # Render gives postgres:// but psycopg2 needs postgresql://
    if DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    import psycopg2
    import psycopg2.extras

    def get_conn():
        return psycopg2.connect(DATABASE_URL, sslmode='require')

    def query_db(sql, args=()):
        conn = get_conn()
        cur  = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql, args)
        rows = cur.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def exec_db(sql, args=()):
        conn = get_conn()
        cur  = conn.cursor()
        cur.execute(sql, args)
        conn.commit()
        conn.close()

    def init_db():
        conn = get_conn()
        c    = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS responses (
            id SERIAL PRIMARY KEY,
            category TEXT NOT NULL,
            logo_name TEXT NOT NULL,
            response TEXT NOT NULL,
            timestamp TEXT NOT NULL)''')
        c.execute('''CREATE TABLE IF NOT EXISTS stars (
            id SERIAL PRIMARY KEY,
            category TEXT NOT NULL UNIQUE,
            logo_name TEXT NOT NULL,
            timestamp TEXT NOT NULL)''')
        c.execute('''CREATE TABLE IF NOT EXISTS feedback (
            id SERIAL PRIMARY KEY,
            playlist_rating INTEGER,
            colour_changes TEXT,
            further_requests TEXT,
            timestamp TEXT NOT NULL)''')
        conn.commit()
        conn.close()

    PH = '%s'  # PostgreSQL placeholder

else:
    # ── LOCAL SQLITE FALLBACK ──
    import sqlite3
    DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logos.db')

    def get_conn():
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

    def query_db(sql, args=()):
        conn = get_conn()
        c    = conn.cursor()
        c.execute(sql, args)
        rows = c.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def exec_db(sql, args=()):
        conn = get_conn()
        conn.execute(sql, args)
        conn.commit()
        conn.close()

    def init_db():
        conn = get_conn()
        c    = conn.cursor()
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
        conn.commit()
        conn.close()

    PH = '?'  # SQLite placeholder

# ── ROUTES ──
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
    d    = request.get_json(force=True)
    cat  = d.get('category','').strip()
    logo = d.get('logo','').strip()
    resp = d.get('response','').strip()
    if not logo or not cat or resp not in ('like','dislike'):
        return jsonify({'status':'error'}), 400
    exec_db(
        f'INSERT INTO responses (category,logo_name,response,timestamp) VALUES ({PH},{PH},{PH},{PH})',
        (cat, logo, resp, datetime.now().isoformat())
    )
    return jsonify({'status':'ok'})

@app.route('/star', methods=['POST'])
def star():
    d      = request.get_json(force=True)
    cat    = d.get('category','').strip()
    logo   = d.get('logo','').strip()
    action = d.get('action','set')
    if not cat: return jsonify({'status':'error'}), 400
    if action == 'clear':
        exec_db(f'DELETE FROM stars WHERE category={PH}', (cat,))
    else:
        if DATABASE_URL:
            exec_db(
                f'''INSERT INTO stars (category,logo_name,timestamp) VALUES ({PH},{PH},{PH})
                    ON CONFLICT(category) DO UPDATE SET logo_name=EXCLUDED.logo_name, timestamp=EXCLUDED.timestamp''',
                (cat, logo, datetime.now().isoformat())
            )
        else:
            exec_db(
                f'''INSERT INTO stars (category,logo_name,timestamp) VALUES ({PH},{PH},{PH})
                    ON CONFLICT(category) DO UPDATE SET logo_name=excluded.logo_name, timestamp=excluded.timestamp''',
                (cat, logo, datetime.now().isoformat())
            )
    return jsonify({'status':'ok'})

@app.route('/feedback', methods=['POST'])
def feedback():
    d        = request.get_json(force=True)
    rating   = d.get('playlist_rating', 0)
    colours  = d.get('colour_changes', '').strip()
    requests = d.get('further_requests', '').strip()
    exec_db(
        f'INSERT INTO feedback (playlist_rating,colour_changes,further_requests,timestamp) VALUES ({PH},{PH},{PH},{PH})',
        (rating, colours, requests, datetime.now().isoformat())
    )
    return jsonify({'status':'ok'})

@app.route('/api/admin-data')
def admin_data():
    votes    = query_db('SELECT * FROM responses ORDER BY timestamp DESC')
    stars    = query_db('SELECT * FROM stars ORDER BY timestamp DESC')
    fb       = query_db('SELECT * FROM feedback ORDER BY timestamp DESC')
    return jsonify({'votes': votes, 'stars': stars, 'feedback': fb})

@app.route('/api/results')
def api_results():
    rows = query_db('''
        SELECT category, logo_name,
               SUM(CASE WHEN response=\'like\'    THEN 1 ELSE 0 END) AS likes,
               SUM(CASE WHEN response=\'dislike\' THEN 1 ELSE 0 END) AS dislikes,
               COUNT(*) AS total
        FROM responses
        GROUP BY category, logo_name
        ORDER BY category, likes DESC''')
    stars = query_db('SELECT category, logo_name FROM stars')
    fb    = query_db('SELECT * FROM feedback ORDER BY id DESC LIMIT 1')
    grouped = {}
    for r in rows:
        grouped.setdefault(r['category'], []).append(r)
    return jsonify({
        'votes':    grouped,
        'stars':    {s['category']: s['logo_name'] for s in stars},
        'feedback': fb[0] if fb else None
    })

@app.route('/api/reset', methods=['POST'])
def reset():
    exec_db('DELETE FROM responses')
    exec_db('DELETE FROM stars')
    exec_db('DELETE FROM feedback')
    return jsonify({'status':'ok'})

# ── INIT ──
init_db()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # This creates the tables automatically on startup
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
