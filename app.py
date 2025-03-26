from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from database import create_connection
from models import Voter, Candidate, Vote
import uuid
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a random secret key

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        voter_id = request.form['voter_id']
        password = request.form['password']
        
        conn = create_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM voters WHERE voter_id = ?", (voter_id,))
        user = cur.fetchone()
        conn.close()

        if user and check_password_hash(user[6], password):
            session['user_id'] = user[0]
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        last_name = request.form['last_name']
        date_of_birth = request.form['date_of_birth']
        phone_number = request.form['phone_number']
        voter_id = request.form['voter_id']
        password = request.form['password']

        conn = create_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM voters WHERE voter_id = ?", (voter_id,))
        existing_user = cur.fetchone()

        if existing_user:
            flash('Voter ID already exists', 'error')
        else:
            hashed_password = generate_password_hash(password)
            cur.execute("INSERT INTO voters (name, last_name, date_of_birth, phone_number, voter_id, password) VALUES (?, ?, ?, ?, ?, ?)",
                        (name, last_name, date_of_birth, phone_number, voter_id, hashed_password))
            conn.commit()
            flash('Registration successful', 'success')
            return redirect(url_for('login'))

        conn.close()

    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = create_connection()
    if conn is None:
        flash('Error connecting to the database', 'error')
        return redirect(url_for('index'))

    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM voters WHERE id = ?", (session['user_id'],))
        user = cur.fetchone()

        cur.execute("SELECT * FROM candidates")
        candidates = cur.fetchall()

        if not candidates:
            # If no candidates are found, add so
            # me sample candidates
            sample_candidates = [
                ('John Doe', 'Party 1', 'john_doe.jpg', 'Promise 1\nPromise 2', 'Assets info', 'Liabilities info', 'Background info', 'Political views', 'Regional views'),
                ('Jane Smith', 'Party B', 'jane_smith.jpg', 'Promise 1\nPromise 2', 'Assets info', 'Liabilities info', 'Background info', 'Political views', 'Regional views'),
            ]
            cur.executemany("""
                INSERT INTO candidates (name, party, photo_url, promises, assets, liabilities, background, political_views, regional_views)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, sample_candidates)
            conn.commit()
            
            # Fetch the newly added candidates
            cur.execute("SELECT * FROM candidates")
            candidates = cur.fetchall()

        return render_template('dashboard.html', user=user, candidates=candidates)
    except sqlite3.Error as e:
        flash(f'An error occurred: {str(e)}', 'error')
        return redirect(url_for('index'))
    finally:
        conn.close()

@app.route('/candidate/<int:candidate_id>')
def candidate_detail(candidate_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = create_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM candidates WHERE id = ?", (candidate_id,))
    candidate = cur.fetchone()
    conn.close()

    return render_template('candidate_detail.html', candidate=candidate)

@app.route('/vote/<int:candidate_id>', methods=['POST'])
def vote(candidate_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = create_connection()
    cur = conn.cursor()
    cur.execute("SELECT has_voted FROM voters WHERE id = ?", (session['user_id'],))
    has_voted = cur.fetchone()[0]

    if has_voted:
        flash('You have already voted', 'error')
        return redirect(url_for('dashboard'))

    reference_number = str(uuid.uuid4())
    timestamp = datetime.now().isoformat()

    cur.execute("INSERT INTO votes (voter_id, candidate_id, timestamp, reference_number) VALUES (?, ?, ?, ?)",
                (session['user_id'], candidate_id, timestamp, reference_number))
    cur.execute("UPDATE voters SET has_voted = 1 WHERE id = ?", (session['user_id'],))
    conn.commit()
    conn.close()

    flash(f'Thank you for voting! Your reference number is {reference_number}', 'success')
    return redirect(url_for('vote_confirmation', reference_number=reference_number))

@app.route('/vote_confirmation/<reference_number>')
def vote_confirmation(reference_number):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    return render_template('vote_confirmation.html', reference_number=reference_number)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)