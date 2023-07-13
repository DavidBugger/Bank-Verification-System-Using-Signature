from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3

app = Flask(__name__)

# Create SQLite database
conn = sqlite3.connect('bank_transactions.db')
c = conn.cursor()

# Create table for user registration
c.execute('''CREATE TABLE IF NOT EXISTS users
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              username TEXT NOT NULL,
              password TEXT NOT NULL,
              signature TEXT NOT NULL)''')
conn.commit()

# Create table for transactions
c.execute('''CREATE TABLE IF NOT EXISTS transactions
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              user_id INTEGER,
              type TEXT,
              amount INTEGER,
              FOREIGN KEY(user_id) REFERENCES users(id))''')
conn.commit()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        signature = request.form['signature']
        
        # Insert user data into database
        c.execute("INSERT INTO users (username, password, signature) VALUES (?, ?, ?)",
                  (username, password, signature))
        conn.commit()
        
        return redirect('/login')
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Fetch user data from database
        c.execute("SELECT id, signature FROM users WHERE username = ? AND password = ?",
                  (username, password))
        user = c.fetchone()
        
        if user:
            session['user_id'] = user[0]
            return redirect('/dashboard')
        else:
            return render_template('login.html', error='Invalid username or password')
    
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        user_id = session['user_id']
        
        # Fetch user data from database
        c.execute("SELECT username, signature FROM users WHERE id = ?", (user_id,))
        user = c.fetchone()
        
        return render_template('dashboard.html', username=user[0], signature=user[1])
    
    return redirect('/login')

@app.route('/deposit', methods=['GET', 'POST'])
def deposit():
    if request.method == 'POST':
        amount = int(request.form['amount'])
        
        # Insert deposit transaction into database
        c.execute("INSERT INTO transactions (user_id, type, amount) VALUES (?, 'Deposit', ?)",
                  (session['user_id'], amount))
        conn.commit()
        
        return redirect('/dashboard')
    
    return render_template('deposit.html')

@app.route('/withdrawal', methods=['GET', 'POST'])
def withdrawal():
    if request.method == 'POST':
        amount = int(request.form['amount'])
        
        # Insert withdrawal transaction into database
        c.execute("INSERT INTO transactions (user_id, type, amount) VALUES (?, 'Withdrawal', ?)",
                  (session['user_id'], amount))
        conn.commit()
        
        return redirect('/dashboard')
    
    return render_template('withdrawal.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__ == '__main__':
    app.secret_key = 'your_secret_key'
    app.run(debug=True)
