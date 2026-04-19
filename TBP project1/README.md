# TBP Project — Deployment & Admin Instructions

This project stores user feedback permanently in MongoDB and provides an admin interface to view feedbacks.

Quick setup (local):

1. Create a virtual environment and install dependencies:

```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

2. Environment variables (recommended):

- `MONGODB_URI` — MongoDB connection string (default: `mongodb://localhost:27017/`).
- `ADMIN_PASSWORD` — password for admin access (default: `admin123`).
- `FLASK_SECRET` — Flask secret key (default used if not set).

Example (Windows PowerShell):

```powershell
$env:MONGODB_URI = "mongodb://localhost:27017/"
$env:ADMIN_PASSWORD = "your_admin_password"
$env:FLASK_SECRET = "a_strong_secret"
python app.py
```

3. Access the app in your browser:

- Home: http://127.0.0.1:5000/
- Admin login: http://127.0.0.1:5000/admin_login
- Admin dashboard (after login): http://127.0.0.1:5000/admin
- Feedbacks JSON (admin only): http://127.0.0.1:5000/feedbacks.json

Notes:

- Feedbacks are saved in the `feedbacks` collection with a UTC `timestamp` field.
- For production, use MongoDB Atlas and set `MONGODB_URI` to the Atlas connection string.
- Run behind a WSGI server (Gunicorn/Waitress) and set secure env variables on the host.

Security reminder:

- Do not expose `ADMIN_PASSWORD` publicly. Use strong secrets and HTTPS in production.

If you want, I can add an admin button into the site header or secure admin actions to use POST requests.```