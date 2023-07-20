from flask import Flask, render_template, request, redirect, session,url_for, flash
from models import db, User, Transaction
from app import app
import os
from werkzeug.utils import secure_filename


# @app.route('/')
# def home():  
#     return render_template('index.html')

# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
#         signature = request.files['signature']
#         # Save the uploaded signature file
#         signature_filename = secure_filename(signature.filename)
#         signature.save(os.path.join(app.config['UPLOAD_FOLDER'], signature_filename))
#         # Insert user data into the database
#         user = User(username=username, password=password, signature=signature_filename)
#         db.session.add(user)
#         db.session.commit()
#         return redirect('/login')

#     return render_template('register.html')


# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
#         signature = request.files['signature']

#         # Retrieve the user from the database
#         user = User.query.filter_by(username=username).first()

#         if user:
#             # Compare the uploaded signature with the one stored in the database
#             uploaded_signature = signature.read()
#             stored_signature_path = os.path.join(app.config['UPLOAD_FOLDER'], user.signature)
#             stored_signature = open(stored_signature_path, 'rb').read()

#             if uploaded_signature == stored_signature:
#                 session['user_id'] = user.id
#                 return redirect('/dashboard')
#             else:
#                 flash('Invalid signature')
#         else:
#             flash('Invalid username or password')

#     return render_template('login.html')


# @app.route('/dashboard')
# def dashboard():
#     # Add your code for the dashboard here
#     pass


# @app.route('/deposit', methods=['GET', 'POST'])
# def deposit():
#     if request.method == 'POST':
#         amount = request.form['amount']

#         # Retrieve the user from the session
#         user_id = session.get('user_id')
#         user = User.query.get(user_id)

#         if user:
#             # Create a new transaction for the deposit
#             deposit = Transaction(user_id=user.id, type='Deposit', amount=amount)
#             db.session.add(deposit)
#             db.session.commit()

#             return redirect('/dashboard')

#     return render_template('deposit.html')


# @app.route('/withdrawal', methods=['GET', 'POST'])
# def withdrawal():
#     if 'user_id' not in session:
#         return redirect('/login')

#     if request.method == 'POST':
#         amount = int(request.form['amount'])

#         user_id = session['user_id']
#         user = User.query.get(user_id)

#         if user:
#             if amount > 0:
#                 if amount <= user.balance:
#                     # Subtract the withdrawal amount from the user's balance
#                     user.balance -= amount
#                     db.session.commit()

#                     # Insert withdrawal transaction into database
#                     transaction = Transaction(user_id=user_id, type='Withdrawal', amount=amount)
#                     db.session.add(transaction)
#                     db.session.commit()

#                     return redirect('/dashboard')
#                 else:
#                     return render_template('withdrawal.html', error='Insufficient balance')
#             else:
#                 return render_template('withdrawal.html', error='Invalid amount')

#     return render_template('withdrawal.html')


@app.route('/logout')
def logout():
    # Add your code for logging out here
    pass
