# You will probably need more methods from flask but this one is a good start.
from flask import render_template, request

# Import things from Flask that we need.
from accounting import app, db

# Import our models
from models import Contact, Invoice, Policy
from tools import PolicyAccounting

# Routing for the server.
@app.route("/")
def index():
    # You will need to serve something up here.
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
