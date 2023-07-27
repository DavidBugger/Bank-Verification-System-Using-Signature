from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    signature = db.Column(db.String(100), nullable=False)
    # balance = db.Column(db.Float, default=0.0)  # Adding the balance column
    transactions = db.relationship('Transaction', backref='user', lazy=True)


class Transaction(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    type = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    
class Customer_Registration(db.Model):
    __tablename__ = 'customer_registration'
    cus_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    account_no = db.Column(db.String(100), nullable=False)
    phone_no = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    signature = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    
class Customer_Login(db.Model):
    __tablename__ = 'customer_login'
    cus_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    signature = db.Column(db.String(100), nullable=False)
    account_no = db.Column(db.String(100), nullable=False)
