from flask import Flask, render_template, request, jsonify, session
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from aiogram import Bot
import config
from db import get_conn, get_pending_proposals, update_proposal_status
from stats import generate_stats_graph
from posting import post_single_photo
import os
import sqlite3

app = Flask(__name__)
app.secret_key = os.getenv('WEB_PANEL_SECRET', 'devkey')

bot = Bot(token=config.BOT_TOKEN)

# Flask-Admin
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy(app)
# Подключи DB (упрощённо для admin)

class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return session.get('logged_in')

admin = Admin(app, name='Bot Panel', index_view=MyAdminIndexView())

# === ВЕБ-ПАНЕЛЬ ===
@app.route('/admin')
def admin_dashboard():
    if not session.get('logged_in'):
        return '<form method=post><input name=password placeholder="Пароль админа"><button>Войти</button></form>'
    proposals = get_pending_proposals()
    graph = generate_stats_graph()
    return render_template('admin.html', proposals=proposals, graph=graph)

@app.route('/admin/login', methods=['POST'])
def login():
    if request.form['password'] == 'admin123':  # Измени!
        session['logged_in'] = True
    return 'OK'  # Redirect JS

@app.route('/admin/approve/<int:prop_id>')
def approve(prop_id):
    update_proposal_status(prop_id, 'approved')
    # Постинг
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT file_path FROM proposals WHERE id=?', (prop_id,))
    path = c.fetchone()[0]
    post_single_photo(bot, path)
    os.remove(path)
    conn.close()
    return jsonify({'status': 'approved'})

# === API для MINI APP ===
@app.route('/api/proposals')
def api_proposals():
    return jsonify(get_pending_proposals())

@app.route('/api/stats')
def api_stats():
    return jsonify({'posts': 42, 'views': 1234})  # Из DB

if __name__ == '__main__':
    app.run(debug=True, port=5000)