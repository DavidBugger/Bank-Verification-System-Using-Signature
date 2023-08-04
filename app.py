
from flask import Flask, render_template, session, redirect, flash
from models import db
from routes import *
from flask_sqlalchemy import SQLAlchemy
import os
import sqlite3
from flask import jsonify

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bank_transactions.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/signatures'  
db.init_app(app)
# Connect to the database (replace 'your_database.db' with the actual path to your SQLite database)
conn = sqlite3.connect('database2.db', check_same_thread=False)
cursor = conn.cursor()

# Create a table called 'users' with the specified fields
cursor.execute('''CREATE TABLE IF NOT EXISTS customer_registration (
                    cust_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    account_no TEXT UNIQUE NOT NULL,
                    signature TEXT NOT NULL,
                    phone_no TEXT  NOT NULL,
                    password TEXT  NOT NULL,
                    address TEXT  NOT NULL
                    
                )''')

# Create a table called 'users' with the specified fields
cursor.execute('''CREATE TABLE IF NOT EXISTS customer_login (
                    cust_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    account_no TEXT UNIQUE NOT NULL,
                    signature TEXT NOT NULL
                )''')

# Commit the changes and close the connection
conn.commit()

# Create a table called 'users' with the specified fields
cursor.execute('''CREATE TABLE IF NOT EXISTS balance (
                    cust_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    customer_balance INTEGER  NOT NULL

                )''')

# Commit the changes and close the connection
conn.commit()


# Directory to store customer signatures
SIGNATURES_DIR = 'static/signatures'

@app.route('/register_customer', methods=['GET', 'POST'])
def register_customer():
    if request.method == 'POST':
        name = request.form['name']
        account_no = request.form['account_no']
        password = request.form['password']
        phone_no = request.form['phone_no']
        address = request.form['address']
        signature = request.files['signature']
        password = request.form['password'] 
           # Check if the account number is an integer
        try:
            account_no = int(account_no)
        except ValueError:
            # flash('Account number must be an integer.', 'danger')
            return redirect(url_for('register_customer'))
        # Check if the account number meets the minimum length requirement (at least 11 characters)
        if len(str(account_no)) < 11:
            # flash('Account number must be at least 11 characters long.', 'danger')
            return redirect(url_for('register_customer'))

        # Save the uploaded signature
        if signature and allowed_file(signature.filename):
            signature_filename = secure_filename(signature.filename)
            signature.save(os.path.join(SIGNATURES_DIR, signature_filename))
        else:
            # Handle error if no signature or invalid file type
            flash('Invalid signature. Please upload a valid image file.', 'danger')
            return redirect(url_for('customer_registration_form'))

        # Insert customer data into the database
        cursor.execute("INSERT INTO customer_registration (name, account_no, signature,phone_no, password, address) VALUES (?, ?, ?, ?, ?, ?)",
                       (name, account_no,signature_filename, phone_no, password, address))
        conn.commit()

        flash('Customer registration successful.', 'success')
        return redirect(url_for('login'))  # Replace 'login' with the route to your login page

    return render_template('register.html')

# List of allowed file extensions for the signature
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    # Check if the file type is allowed based on the file extension
    # We assume the file extension is after the last dot in the filename
    file_extension = filename.rsplit('.', 1)[1].lower() if '.' in filename else None
    return file_extension in ALLOWED_EXTENSIONS

def secure_filename(filename):
    # Sanitize the filename to remove any potentially dangerous characters
    # We'll replace any characters not in [a-zA-Z0-9.-_] with underscores
    secure_name = ''.join(c if c.isalnum() or c in '-_.' else '_' for c in filename)
    return secure_name



@app.route('/')
def home():
    return render_template('index2.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        signature = request.files['signature']
        # Save the uploaded signature file
        signature_filename = secure_filename(signature.filename)
        signature.save(os.path.join(app.config['UPLOAD_FOLDER'], signature_filename))
        # Insert user data into the database
        user = User(username=username, password=password, signature=signature_filename)
        db.session.add(user)
        db.session.commit()
        return redirect('/login')

    return render_template('register.html')

# Directory to store user signatures
UPLOAD_FOLDER = 'static/signatures'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        account_no = request.form['account_no']
        signature = request.files['signature']
        # Retrieve the user from the database based on the provided account number
        cursor.execute("SELECT * FROM customer_registration WHERE account_no = ?", (account_no,))
        user = cursor.fetchone()
        if user:
            # Compare the uploaded signature with the one stored in the database
            uploaded_signature = signature.read()
            stored_signature_path = os.path.join(app.config['UPLOAD_FOLDER'], user[3])  # Assuming signature path is stored in column 5
            stored_signature = open(stored_signature_path, 'rb').read()
            
            if uploaded_signature == stored_signature:
                # Signature matches, user is authenticated
                session['cust_id'] = user[0]  # Assuming user ID is stored in column 0
                return redirect('/dashboard')  # Replace '/dashboard' with the route to your dashboard page
            else:
                flash('Invalid signature', 'danger')
        else:
            flash('Invalid account number', 'danger')

    return render_template('login.html')


@app.route('/deposit', methods=['GET', 'POST'])
def deposit():
    if request.method == 'POST':
        amount = int(request.form['amount'])
        # Retrieve the username from the session
        username = session.get('account_no')
        # Query the customer_registration table to get the cust_id
        cursor = conn.cursor()
        cursor.execute('''
            SELECT cust_id FROM customer_registration WHERE account_no = ?
        ''', (username,))
        cust_id = cursor.fetchone()
        # Update the user's balance in the customer_balance table
        cursor.execute('''
            INSERT INTO balance (cust_id, balance) VALUES (?, ?)
            ON CONFLICT (cust_id) DO UPDATE SET balance = balance + ?
        ''', (cust_id, amount, amount))
        conn.commit()

        # Use jsonify to send the response data to the frontend
        response_data = {'status': 'success', 'amount': amount}
        return jsonify(response_data)

    return render_template('deposit.html')



@app.route('/dashboard')
def dashboard():
    balance = get_balance()
    return render_template('dashboard.html', balance=balance)


def get_total_transactions_and_balance(user_id):
    # Get the total number of transactions for the user
    total_transactions = Transaction.query.filter_by(user_id=user_id).count()
    # Get the sum of amounts for all transactions of the user
    total_amount = db.session.query(db.func.sum(Transaction.amount)).filter_by(user_id=user_id).scalar()
    # If there are no transactions for the user, set the total amount to 0
    total_amount = total_amount or 0
    return total_transactions, total_amount



# Function to retrieve balance for a specific username
def get_balance():
    username = session.get('cust_id')
    if not username:
        return None  # If no username is found in the session, return None
    # Assuming 'balance' is the column name in the 'balance' table
    cursor.execute('SELECT balance FROM balance WHERE cust_id = ?', (username,))
    balance = cursor.fetchone()  # Fetch the first row as a tuple
    
# @app.route('/withdraw', methods=['POST', 'GET'])
@app.route('/withdraw', methods=['POST', 'GET'])
def withdraw():
    if request.method == 'POST':
        amount = int(request.form['amount'])

        # Retrieve the username from the session
        username = session.get('account_no')

        # Query the customer_registration table to get the cust_id
        cursor = conn.cursor()
        cursor.execute('''
            SELECT cust_id FROM customer_registration WHERE account_no = ?
        ''', (username,))
        cust_id = cursor.fetchone()

        # Check if the user has enough balance to withdraw
        cursor.execute('''
            SELECT balance FROM balance WHERE cust_id = ?
        ''', (cust_id,))
        balance = cursor.fetchone()
        if balance and balance >= amount:
            # Perform the withdrawal
            # Convert the tuple to a list before binding it to the parameter
            amount_list = list(amount)
            cursor.execute('''
                UPDATE balance SET balance = balance - ? WHERE cust_id = ?
            ''', (amount_list, cust_id))
            conn.commit()

            # Use jsonify to send the response data to the frontend
            response_data = {'status': 'success', 'amount': amount}
            return jsonify(response_data)
        else:
            # Return an error message if the user does not have enough balance
            response_data = {'status': 'error', 'message': 'Insufficient balance for withdrawal'}
            return jsonify(response_data)

    return render_template('withdrawal.html')

@app.route('/transfer', methods=['POST', 'GET'])
def transfer():
    if request.method == 'POST':
        amount = int(request.form['amount'])
        receiver_username = request.form['account_no']
        # Retrieve the cust_id of the sender from the session
        sender_username = session.get('cust_id')
        cursor = conn.cursor()

        # Query the customer_registration table to get the cust_id of the sender
        cursor.execute('''
            SELECT cust_id FROM customer_registration WHERE cust_id = ?
        ''', (sender_username,))
        sender_cust_id = cursor.fetchone()

        if sender_cust_id:
            sender_cust_id = sender_cust_id[0]
            # Query the customer_registration table to get the cust_id of the receiver
            cursor.execute('''
                SELECT cust_id FROM customer_registration WHERE account_no = ?
            ''', (receiver_username,))
            receiver_cust_id = cursor.fetchone()

            if receiver_cust_id:
                receiver_cust_id = receiver_cust_id[0]
                # Fetch the sender's balance from the customer_balance table
                cursor.execute('''
                    SELECT balance FROM balance WHERE cust_id = ?
                ''', (sender_cust_id,))
                sender_balance = cursor.fetchone()[0]

                if sender_balance >= amount:
                    # Perform the transfer by updating balances in the customer_balance table
                    cursor.execute('''
                        UPDATE balance SET balance = balance - ? WHERE cust_id = ?
                    ''', (amount, sender_cust_id))
                    cursor.execute('''
                        UPDATE balance SET balance = balance + ? WHERE cust_id = ?
                    ''', (amount, receiver_cust_id))
                    conn.commit()

                    # Use jsonify to send the response data to the frontend
                    response_data = {'status': 'success', 'amount': amount, 'receiver_username': receiver_username}
                    return jsonify(response_data)
                else:
                    # Use jsonify to send the response data to the frontend
                    response_data = {'status': 'error', 'message': 'Insufficient balance for transfer'}
                    return jsonify(response_data)
            else:
                # Use jsonify to send the response data to the frontend
                response_data = {'status': 'error', 'message': 'Receiver not found'}
                return jsonify(response_data)
        else:
            # Use jsonify to send the response data to the frontend
            response_data = {'status': 'error', 'message': 'Sender not found'}
            return jsonify(response_data)

    return render_template('transfer.html')





if __name__ == '__main__':
    with app.app_context():
        app.secret_key = 'hello'
        db.create_all()
        app.run(debug=True)
