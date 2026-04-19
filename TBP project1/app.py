from flask import Flask, render_template, request, redirect, session, url_for, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
import os
import datetime

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", "secret123")

# Environment-configurable MongoDB connection (use MongoDB Atlas in production)
MONGODB_URI = os.environ.get("MONGODB_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGODB_URI)
db = client["tbp_project"]
users = db["users"]
feedbacks = db["feedbacks"]

# Admin password (set via environment variable in deployment)
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123")

# ---------------- ROUTES ---------------- #

# Home
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/content')
def content():
    return render_template('content.html')

@app.route('/quiz')
def quiz():
    return render_template('quiz.html')

@app.route('/games')
def games():
    return render_template('games.html')

@app.route('/spin')
def spin():
    return render_template('spin.html')

@app.route('/card')
def card():
    return render_template('card.html')

@app.route('/match')
def match():
    return render_template('match.html')

@app.route('/resources')
def resources():
    return render_template('resources.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')


# ---------------- AUTH ---------------- #

# Signup
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        if users.find_one({"email": email}):
            return "User already exists!"

        users.insert_one({
            "name": name,
            "email": email,
            "password": password
        })

        return redirect(url_for('login'))

    return render_template("signup.html")


# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = users.find_one({"email": email, "password": password})

        if user:
            session["user"] = user["name"]
            return redirect(url_for('home'))

        return "Invalid credentials!"

    return render_template("login.html")


# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


# ---------------- ADMIN ---------------- #

@app.route('/admin')
def admin_dashboard():
    if "admin" in session:
        all_users = list(users.find())
        all_feedbacks = list(feedbacks.find())
        return render_template("admin.html", users=all_users, feedbacks=all_feedbacks)
    return redirect(url_for('login'))


# Delete user
@app.route('/delete_user/<email>')
def delete_user(email):
    if "admin" in session:
        users.delete_one({"email": email})
        return redirect(url_for('admin_dashboard'))
    return "Unauthorized"


# ---------------- FEEDBACK ---------------- #

@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    name = request.form['name']
    email = request.form.get('email')
    message = request.form['message']

    feedbacks.insert_one({
        "name": name,
        "email": email,
        "message": message,
        "timestamp": datetime.datetime.utcnow()
    })

    return redirect(url_for('contact'))


# Admin login (separate from regular user login)
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password and password == ADMIN_PASSWORD:
            session['admin'] = True
            return redirect(url_for('admin_dashboard'))
        return "Invalid admin password!"

    return render_template('admin_login.html')


# JSON endpoint for feedbacks (admin only)
@app.route('/feedbacks.json')
def feedbacks_json():
    if "admin" in session:
        docs = list(feedbacks.find())
        out = []
        for d in docs:
            out.append({
                "id": str(d.get("_id")),
                "name": d.get("name"),
                "email": d.get("email"),
                "message": d.get("message"),
                "timestamp": d.get("timestamp").isoformat() if d.get("timestamp") else None
            })
        return jsonify(out)
    return jsonify({"error": "unauthorized"}), 401


@app.route('/admin_auth', methods=['POST'])
def admin_auth():
    # Accept JSON or form data
    password = None
    if request.is_json:
        password = request.json.get('password')
    else:
        password = request.form.get('password')

    if password and password == ADMIN_PASSWORD:
        session['admin'] = True
        return jsonify({"ok": True})
    return jsonify({"ok": False}), 401


@app.route('/delete_feedback', methods=['POST'])
def delete_feedback():
    if "admin" not in session:
        return jsonify({"error": "unauthorized"}), 401
    data = request.get_json() or request.form
    fid = data.get('id')
    if not fid:
        return jsonify({"error": "missing id"}), 400
    try:
        feedbacks.delete_one({"_id": ObjectId(fid)})
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/delete_all_feedbacks', methods=['POST'])
def delete_all_feedbacks():
    if "admin" not in session:
        return jsonify({"error": "unauthorized"}), 401
    feedbacks.delete_many({})
    return jsonify({"ok": True})


# ---------------- RUN ---------------- #

if __name__ == '__main__':
    app.run(debug=True)