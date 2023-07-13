from flask import Flask, render_template
from models import db
from routes import *
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

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.secret_key = 'hello'
    app.run(debug=True)
