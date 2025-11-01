from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

# === ПУТЬ К БАЗЕ ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "bot.db")

# === FLASK ===
app = Flask(__name__)

# === КОНФИГ ДО SQLALCHEMY ===
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# === SQLALCHEMY ПОСЛЕ КОНФИГА ===
db = SQLAlchemy(app)

# === МОДЕЛЬ ===
class Proposal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    file_id = db.Column(db.String)
    file_type = db.Column(db.String)
    status = db.Column(db.String, default='pending')
    timestamp = db.Column(db.String)

# === МАРШРУТЫ ===
@app.route('/')
def index():
    proposals = Proposal.query.filter_by(status='pending').all()
    return render_template('admin.html', proposals=proposals)

@app.route('/approve/<int:prop_id>')
def approve(prop_id):
    prop = Proposal.query.get(prop_id)
    if prop:
        prop.status = 'approved'
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/reject/<int:prop_id>')
def reject(prop_id):
    prop = Proposal.query.get(prop_id)
    if prop:
        prop.status = 'rejected'
        db.session.commit()
    return redirect(url_for('index'))

# === ЗАПУСК ===
def run_flask():
    with app.app_context():
        db.create_all()
    app.run(port=5000, debug=False, use_reloader=False)

if __name__ == '__main__':
    run_flask()