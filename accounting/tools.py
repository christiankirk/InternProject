#!/user/bin/env python2.7

from datetime import date, datetime
from dateutil.relativedelta import relativedelta

from accounting import db
from models import Contact, Invoice, Payment, Policy

"""
#######################################################
This is the base code for the intern project.

If you have any questions, please contact Amanda at:
    amanda@britecore.com
#######################################################
"""

class PolicyAccounting(object):
    """
     Each policy has its own instance of accounting.
    """
    def __init__(self, policy_id): #Constructor defining arguments or PolicyAccounting
        self.policy = Policy.query.filter_by(id=policy_id).one()

        if not self.policy.invoices: #If there are no invoices create invoices
            self.make_invoices()

    def return_account_balance(self, date_cursor=None): #Returning the account balance
        if not date_cursor: #If there is not date specified, then create time and the date when it is being accessed
            date_cursor = datetime.now().date()

        invoices = Invoice.query.filter_by(policy_id=self.policy.id)\
                                .filter(Invoice.bill_date < date_cursor)\
                                .order_by(Invoice.bill_date)\
                                .all()
        due_now = 0 #Variable to set up the amount due
        for invoice in invoices:
            due_now += invoice.amount_due #Adding to due_now by accessing the amount due on the invoices

        payments = Payment.query.filter_by(policy_id=self.policy.id)\ #Finding the payments that have already been made
                                .filter(Payment.transaction_date < date_cursor)\
                                .all()
        for payment in payments:
            due_now -= payment.amount_paid #Subtracting the payments already made from the amount_due

        return due_now #returning the account balance that needs to still be paid

    def make_payment(self, contact_id=None, date_cursor=None, amount=0): #Function for making a payment on account
        if not date_cursor:
            date_cursor = datetime.now().date()

        if not contact_id: #If there is no contact_id then create one from the name_insured of the poilcy
            try:
                contact_id = self.policy.named_insured
            except:
                pass

        payment = Payment(self.policy.id, #Specifying for payment the policy.id, contact_id, amount, and date
                          contact_id,
                          amount,
                          date_cursor)
        db.session.add(payment)
        db.session.commit() #Committing the amount of the payment

        return payment #Returns the payment received

    def evaluate_cancellation_pending_due_to_non_pay(self, date_cursor=None):
        if not date_cursor:
            date_cursor = datetime.now().date()
        
        invoices = Invoice.query.filter_by(policy_id=self.policy.id)\
            .filter(Invoice.cancel_date <= date_cursor)\
            .order_by(Invoice.bill_date)\
            .all()
        
        for invoice in invoices: #For every invoice if there is an amount returned then the cancellation is pending until the cancel date
            if self.return_account_balance(invoice.cancel_date):
                print "THIS POLICY IS IN CANCELLATION DUE TO NON PAY. ONLY AN AGENT MAY MAKE A PAYMENT"
            else:
                print "THIS POLICY SHOULD NOT CANCEL"

    def evaluate_cancel(self, date_cursor=None): #Function for cancelling an account
        if not date_cursor:
            date_cursor = datetime.now().date()

        invoices = Invoice.query.filter_by(policy_id=self.policy.id)\ #Creating invoices that the policy_id=self.policy.id
                                .filter(Invoice.cancel_date <= date_cursor)\ #Filter by the invoice cancel date is less than or equal to the date specified or created
                                .order_by(Invoice.bill_date)\
                                .all()

        for invoice in invoices: #For every invoice check to see if the invoice is not the same as self.return_account_balance(invoice.cancel_date)
            if not self.return_account_balance(invoice.cancel_date):
                continue
            else:
                date_cancelled = datetime.now().date()
                new_status = Policy.query.filter_by(policy_number).first()
                new_status.status = 'Cancelled'
                print "THIS POLICY WAS CANCELLED ON: ", date_cancelled
                break
        else:
            print "THIS POLICY SHOULD NOT CANCEL"


    def make_invoices(self): #Function to make invoices with no arguments
        for invoice in self.policy.invoices:
            invoice.delete()

        billing_schedules = {'Annual': None, 'Semi-Annual': 3, 'Quarterly': 4, 'Monthly': 12} #Creating a dictionary that specifies the definitions of each word

        invoices = [] #Creating a list names invoices
        first_invoice = Invoice(self.policy.id, #Creating the first invoice from using Invoice() from models.py
                                self.policy.effective_date, #bill_date
                                self.policy.effective_date + relativedelta(months=1), #due date
                                self.policy.effective_date + relativedelta(months=1, days=14), #cancel date two weeks after
                                self.policy.annual_premium) #Amount due
        invoices.append(first_invoice) #Placing first invoice into the list named invoices

        if self.policy.billing_schedule == "Annual": #If the billing schedule is equal to Annual then pass
            pass
        elif self.policy.billing_schedule == "Two-Pay": #Else if the billing schedule is equto to Two-Pay
            first_invoice.amount_due = first_invoice.amount_due / billing_schedules.get(self.policy.billing_schedule) #Figuring out amount due from first invoice
            for i in range(1, billing_schedules.get(self.policy.billing_schedule)): #For every object in the range(starting at one,stopping at billing schedule)
                months_after_eff_date = i*6 #Multiplies by 6 to split 12 months into two payments
                bill_date = self.policy.effective_date + relativedelta(months=months_after_eff_date)
                invoice = Invoice(self.policy.id, #Create an invoice for this specification
                                  bill_date,
                                  bill_date + relativedelta(months=1),
                                  bill_date + relativedelta(months=1, days=14),
                                  self.policy.annual_premium / billing_schedules.get(self.policy.billing_schedule))
                invoices.append(invoice)
        elif self.policy.billing_schedule == "Quarterly": #Else if billing schedule is Quarterly
            first_invoice.amount_due = first_invoice.amount_due / billing_schedules.get(self.policy.billing_schedule)
            for i in range(1, billing_schedules.get(self.policy.billing_schedule)):
                months_after_eff_date = i*3 #Multiplies by 3 to split 12 months into 4 payments
                bill_date = self.policy.effective_date + relativedelta(months=months_after_eff_date)
                invoice = Invoice(self.policy.id,
                                  bill_date,
                                  bill_date + relativedelta(months=1),
                                  bill_date + relativedelta(months=1, days=14),
                                  self.policy.annual_premium / billing_schedules.get(self.policy.billing_schedule))
                invoices.append(invoice)
        elif self.policy.billing_schedule == "Monthly": #Else if billing schedule is Monthly
            first_invoice.amount_due = first_invoice.amount_due / billing_schedules.get(self.policy.billing_schedule)
            for i in range(1, billing_schedules.get(self.policy.billing_schedule)):
                months_after_eff_date = i*1 #Changing variable i to be multiplied by 1 so we have 12 monthly invoices
                bill_date = self.policy.effective_date + relativedelta(months=months_after_eff_date)
                invoice = Invoice(self.policy.id,
                                  bill_date,
                                  bill_date + relativedelta(months=1),
                                  bill_date + relativedelta(months=1, days=14),
                                  self.policy.annual_premium / billing_schedules.get(self.policy.billing_schedule))
                invoices.append(invoice)
        else:
            print "You have chosen a bad billing schedule." #If all the if and elif statements are False then print a bad billing schedule

        for invoice in invoices: #For every invoice add the invoice and commit to database
            db.session.add(invoice)
        db.session.commit()

################################
# The functions below are for the db and 
# shouldn't need to be edited.
################################
def build_or_refresh_db():
    db.drop_all()
    db.create_all()
    insert_data()
    print "DB Ready!"

def insert_data():
    #Contacts
    contacts = []
    john_doe_agent = Contact('John Doe', 'Agent')
    contacts.append(john_doe_agent)
    john_doe_insured = Contact('John Doe', 'Named Insured')
    contacts.append(john_doe_insured)
    bob_smith = Contact('Bob Smith', 'Agent')
    contacts.append(bob_smith)
    anna_white = Contact('Anna White', 'Named Insured')
    contacts.append(anna_white)
    joe_lee = Contact('Joe Lee', 'Agent')
    contacts.append(joe_lee)
    ryan_bucket = Contact('Ryan Bucket', 'Named Insured')
    contacts.append(ryan_bucket)

    for contact in contacts:
        db.session.add(contact)
    db.session.commit()

    policies = []
    p1 = Policy('Policy One', date(2015, 1, 1), 365)
    p1.billing_schedule = 'Annual'
    p1.agent = bob_smith.id
    policies.append(p1)

    p2 = Policy('Policy Two', date(2015, 2, 1), 1600)
    p2.billing_schedule = 'Quarterly'
    p2.named_insured = anna_white.id
    p2.agent = joe_lee.id
    policies.append(p2)

    p3 = Policy('Policy Three', date(2015, 1, 1), 1200)
    p3.billing_schedule = 'Monthly'
    p3.named_insured = ryan_bucket.id
    p3.agent = john_doe_agent.id
    policies.append(p3)

    p4 = Policy('Policy Four', date(2015, 2, 1), 500) #creating policy 4 with given information
    p4.billing_schedule = 'Two-Pay'
    p4.name_insured = ryan_bucket.id
    p4.agent = john_doe_agent.id
    policies.append(p4)

    p5 = Policy('Policy Four', date(2015, 2, 1), 500) #Created another policy 4 for Bob Smith's client
    p5.bill_schedule = 'Two-Pay'
    p5.name_insured = john_doe_insured.id
    p5.agent = bob_smith.id
    policies.append(p5)

    for policy in policies:
        db.session.add(policy)
    db.session.commit()

    for policy in policies:
        PolicyAccounting(policy.id)

    payment_for_p2 = Payment(p2.id, anna_white.id, 400, date(2015, 2, 1))
    db.session.add(payment_for_p2)
    db.session.commit()

