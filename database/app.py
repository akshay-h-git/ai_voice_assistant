from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Initialize the database
def init_db():
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            gemini_api TEXT,
            weather_api TEXT,
            news_api TEXT,
            wake_word TEXT,
            webpage_name TEXT,
            webpage_url TEXT,
            desktop_name TEXT,
            desktop_path TEXT,
            music_name TEXT,
            music_url TEXT,
            FOREIGN KEY(email) REFERENCES users(email)
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/documentation')
def documentation():
    return render_template('doc.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/setup')
def setup():
    return render_template('setup.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['full_name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return render_template('register.html')

        hashed_password = generate_password_hash(password)

        conn = sqlite3.connect('database.db')
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                        (name, email, hashed_password))
            conn.commit()
            flash("Registered successfully. Please login.", "success")
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash("Email already exists.", "error")
        finally:
            conn.close()
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect('database.db')
        cur = conn.cursor()
        cur.execute("SELECT password FROM users WHERE email=?", (email,))
        row = cur.fetchone()
        conn.close()

        if row and check_password_hash(row[0], password):
            session['email'] = email
            return redirect(url_for('settings'))
        else:
            flash("Invalid credentials")
    return render_template('login.html')

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    email = session.get('email')
    if not email:
        return redirect(url_for('login'))

    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    # Get user's name
    cur.execute("SELECT name FROM users WHERE email = ?", (email,))
    user_row = cur.fetchone()
    name = user_row[0] if user_row else "User"

    if request.method == 'POST':
        # Get form data
        form_data = (
            email,
            request.form.get('gemini_api'),
            request.form.get('weather_api'),
            request.form.get('news_api'),
            request.form.get('wake_word', 'Python'),
            request.form.get('webpage_name'),
            request.form.get('webpage_url'),
            request.form.get('desktop_name'),
            request.form.get('desktop_path'),
            request.form.get('music_name'),
            request.form.get('music_url')
        )

        try:
            # Check if settings exist for this user
            cur.execute("SELECT id FROM settings WHERE email = ?", (email,))
            existing = cur.fetchone()

            if existing:
                cur.execute("""
                    UPDATE settings SET
                        gemini_api = ?, weather_api = ?, news_api = ?, wake_word = ?,
                        webpage_name = ?, webpage_url = ?, desktop_name = ?, desktop_path = ?,
                        music_name = ?, music_url = ?
                    WHERE email = ?
                """, form_data[1:] + (email,))
            else:
                cur.execute(""" 
                    INSERT INTO settings 
                    (email, gemini_api, weather_api, news_api, wake_word, webpage_name, 
                    webpage_url, desktop_name, desktop_path, music_name, music_url) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, form_data)

            conn.commit()
            flash("Settings updated successfully!", "success")
            return redirect(url_for('login'))
        except Exception as e:
            flash(f"Error saving settings: {e}", "error")

    # Fetch settings to pre-fill form
    cur.execute("SELECT * FROM settings WHERE email = ?", (email,))
    user_settings = cur.fetchone()

    conn.close()
    return render_template('settings.html', email=email, name=name, user_settings=user_settings)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
