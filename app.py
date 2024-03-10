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
    error = None  # Define an error variable
    if request.method == 'POST':
        username = request.form['username']
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        if user:
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            error = 'User not found'  # Set the error message if user is not found
    return render_template('login.html', error=error)



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
            encrypted_msg_hex = format(encrypted_msg, 'x')
            conn.execute('INSERT INTO messages (sender, recipient, message) VALUES (?, ?, ?)',(session['username'], recipient, encrypted_msg_hex))
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
@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    conn = get_db_connection()
    messages = conn.execute('SELECT sender, message, created_at FROM messages WHERE recipient = ? ORDER BY created_at DESC', (username,)).fetchall()
    conn.close()

    # Organize messages by sender
    messages_by_sender = {}
    for msg in messages:
        sender = msg['sender']
        if sender not in messages_by_sender:
            messages_by_sender[sender] = []
        messages_by_sender[sender].append({'message': msg['message'], 'created_at': msg['created_at']})

    return render_template('dashboard.html', username=username, messages_by_sender=messages_by_sender)


if __name__ == '__main__':
    app.run(debug=True)
