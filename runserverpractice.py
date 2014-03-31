from flask import Flask
from flask import render_template, request
from flask.ext.sqlalchemy import SQLAlchemy
import os
from accounting import app, db
from models import Contact, Invoice, Policy
from tools import PolicyAccounting

app = Flask(__name__)
app.config.from_pyfile('config.py')
db = SQLAlchemy(app)



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/policy', methods=['POST'])
def policy_number():
    policy_number = request.form['policynumber']
    #print("the number is: ", policy_number)
    return render_template('policy.html')

def policy_date():
    policy_date = request.form['policydate']
    #print("the number is: ", policy_number)
    return render_template('policy.html')

def createdb():
    from accounting import db
    db.create_all()

def account_balance(date):
    return PolicyAccounting('Policy One').return_account_balance(date)
    

if __name__=='__main__':
    #account_balance(policy_number)
    createdb()
    port = int(os.environ.get('PORT', 5000))

    if port == 5000:
        app.debug = True

    app.run(host='0.0.0.0', port=port)
