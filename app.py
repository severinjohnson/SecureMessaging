from flask import Flask, render_template, request, redirect, url_for, session
from main import generate_keypair, encrypt, decrypt
import sqlite3
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # For session management

def get_db_connection():
    conn = sqlite3.connect('app.db')
    conn.row_factory = sqlite3.Row  # This enables column access by name: row['column_name']
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        public_key, private_key = generate_keypair(2048)
        conn = get_db_connection()
        conn.execute('INSERT INTO users (username, public_key_n, public_key_e) VALUES (?, ?, ?)',
                     (username, str(public_key[1]), public_key[0]))
        conn.commit()
        conn.close()
        # Show private key to user and instruct them to write it down
        return render_template('show_private_key.html', private_key=private_key)
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        if user:
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            return 'User not found', 404
    return render_template('login.html')


@app.route('/send_message', methods=['GET', 'POST'])
def send_message():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        recipient = request.form['recipient']
        message = request.form['message']
        conn = get_db_connection()
        recipient_public_key = conn.execute('SELECT public_key_n, public_key_e FROM users WHERE username = ?', (recipient,)).fetchone()
        if recipient_public_key:
            encrypted_msg = encrypt((recipient_public_key['public_key_e'], int(recipient_public_key['public_key_n'])), message)
            conn.execute('INSERT INTO messages (sender, recipient, message) VALUES (?, ?, ?)', (session['username'], recipient, encrypted_msg))
            conn.commit()
            conn.close()
            return redirect(url_for('dashboard'))
        else:
            conn.close()
            return 'Recipient not found', 404
    else:
        # This is the part where you fetch the list of users for the GET request
        users = get_all_users()  # Fetch the list of users from the database
        return render_template('send_message.html', users=users)

@app.route('/decrypt_message', methods=['GET', 'POST'])
def decrypt_message():
    if 'username' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        private_key_d = int(request.form['private_key_d'])
        private_key_n = int(request.form['private_key_n'])
        encrypted_msg = int(request.form['encrypted_message'])
        decrypted_message = decrypt((private_key_d, private_key_n), encrypted_msg)
        return render_template('decrypted_message.html', decrypted_message=decrypted_message)
    return render_template('decrypt_message.html')

def get_all_users():
    conn = get_db_connection()
    users = conn.execute('SELECT username FROM users').fetchall()
    conn.close()
    return users

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    username = session['username']
    conn = get_db_connection()
    # Fetch messages for the logged-in user
    user_messages = conn.execute('SELECT * FROM messages WHERE recipient = ?', (username,)).fetchall()
    # Fetch all users for the potential search/display functionality
    user_records = conn.execute('SELECT username FROM users').fetchall()
    conn.close()
    # Pass both user messages and user records to the template
    return render_template('dashboard.html', username=username, messages=user_messages, users=user_records)

if __name__ == '__main__':
    app.run(debug=True)
