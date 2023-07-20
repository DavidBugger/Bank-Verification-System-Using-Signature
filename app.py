# from flask import Flask, render_template, session, redirect, flash
# from models import db,User, Transaction
# from routes import *
# from flask_sqlalchemy import SQLAlchemy
# import os
# # from flask_migrate import Migrate

from flask import Flask, render_template, session, redirect, flash
from models import db
from routes import *
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bank_transactions.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/signatures'  
db.init_app(app)


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


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        signature = request.files['signature']

        # Retrieve the user from the database
        user = User.query.filter_by(username=username).first()

        if user:
            session['username'] = user.username
            session['signature'] = user.signature
            # Compare the uploaded signature with the one stored in the database
            uploaded_signature = signature.read()
            stored_signature_path = os.path.join(app.config['UPLOAD_FOLDER'], user.signature)
            stored_signature = open(stored_signature_path, 'rb').read()

            if uploaded_signature == stored_signature:
                session['user_id'] = user.id
                return redirect('/dashboard')
            else:
                flash('Invalid signature')
        else:
            flash('Invalid username or password')

    return render_template('login.html')



@app.route('/deposit', methods=['GET', 'POST'])
def deposit():
    if request.method == 'POST':
        amount = int(request.form['amount'])
        # Retrieve the username from the session
        username = session['username']
        # Fetch the user from the Users model using the username
        user = User.query.filter_by(username=username).first()
        if user and session['user_id'] == user.id:
            # Create a new transaction for the deposit
            deposit = Transaction(user_id=user.id, type='Deposit', amount=amount)
            db.session.add(deposit)
            db.session.commit()
            flash(f'Deposit successful! Amount: {amount}', 'success')
        else:
            flash('Invalid user or session', 'danger')

        return redirect('/dashboard')

    return render_template('deposit.html')

@app.route('/dashboard')
def dashboard():
    # Retrieve the user from the session
    username = session.get('username')
    user = User.query.filter_by(username=username).first()
    if user:
        # Query the database to get the total number of records for the logged-in user
        total_records = Transaction.query.filter_by(user_id=user.id).count()
        # Get the total number of transactions and total amount for the user
        total_transactions, total_amount = get_total_transactions_and_balance(user.id)
        # Get the sum of amounts for all transactions of the user
        total_amount = db.session.query(db.func.sum(Transaction.amount)).filter_by(user_id=user.id).scalar()
        remaining_balance = total_amount if total_amount is not None else 0
        return render_template('dashboard.html', total_records=total_records, username=username,user=user, total_transactions=total_transactions, total_amount=total_amount,remaining_balance=remaining_balance)
    return render_template('dashboard.html', total_records)


def get_total_transactions_and_balance(user_id):
    # Get the total number of transactions for the user
    total_transactions = Transaction.query.filter_by(user_id=user_id).count()
    # Get the sum of amounts for all transactions of the user
    total_amount = db.session.query(db.func.sum(Transaction.amount)).filter_by(user_id=user_id).scalar()
    # If there are no transactions for the user, set the total amount to 0
    total_amount = total_amount or 0
    return total_transactions, total_amount


@app.route('/withdraw', methods=['GET', 'POST'])
def withdraw():
    if request.method == 'POST':
        amount = int(request.form['amount'])
        # Retrieve the user from the session
        username = session.get('id')
        # Fetch the user from the Users model
        user = Transaction.query.filter_by(user_id=username).first()
        if user:
            if user.amount >= amount:
                # Create a new transaction for the withdrawal
                withdrawal = Transaction(user_id=user.id, type='Withdrawal', amount=amount)
                db.session.add(withdrawal)
                # Update the user's balance
                user.amount -= amount
                db.session.commit()

                flash(f'Withdrawal successful! Remaining balance: {user.amount}', 'success')
            else:
                flash('Insufficient balance for withdrawal', 'danger')

            return redirect(url_for('dashboard'))

    return render_template('withdrawal.html')


@app.route('/transfer', methods=['GET', 'POST'])
def transfer():
    if request.method == 'POST':
        amount = int(request.form['amount'])
        sender_username = session.get('user_id')
        receiver_username = request.form['receiver']

        # Fetch the sender and receiver from the Transactions model
        sender = Transaction.query.filter_by(user_id=sender_username).first()
        receiver = Transaction.query.filter_by(user_id=receiver_username).first()

        if sender and receiver:
            if sender.amount >= amount:
                # Update the sender's balance
                sender.amount -= amount
                db.session.commit()

                # Update the receiver's balance
                receiver.amount += amount
                db.session.commit()

                # Create transactions for both sender and receiver
                sender_transaction = Transaction(user_id=sender.user_id, type='Transfer (To ' + receiver_username + ')', amount=-amount)
                receiver_transaction = Transaction(user_id=receiver.user_id, type='Transfer (From ' + sender_username + ')', amount=amount)
                db.session.add(sender_transaction)
                db.session.add(receiver_transaction)
                db.session.commit()

                flash(f'Transfer successful! Transferred {amount} to {receiver_username}', 'success')
            else:
                flash('Insufficient balance for transfer', 'danger')
        else:
            flash('Sender or receiver not found', 'danger')

        return redirect('/dashboard')

    return render_template('transfer.html')



if __name__ == '__main__':
    with app.app_context():
        app.secret_key = 'hello'
        app.run(debug=True)
