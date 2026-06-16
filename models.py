from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class Admin(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    mobile_number = db.Column(db.String(20), nullable=False)
    alternate_number = db.Column(db.String(20))
    address = db.Column(db.Text)
    joining_date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)
    monthly_fee = db.Column(db.Float, nullable=False)
    payment_due_date = db.Column(db.Integer, nullable=False) # Day of the month (1-31)
    status = db.Column(db.String(20), nullable=False, default='Active') # Active, Inactive
    notes = db.Column(db.Text)
    
    attendances = db.relationship('Attendance', backref='customer', lazy=True)
    payments = db.relationship('Payment', backref='customer', lazy=True)

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)
    status = db.Column(db.String(20), nullable=False) # Present, Absent, Late

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)
    payment_method = db.Column(db.String(50)) # Cash, UPI, Bank Transfer
    status = db.Column(db.String(20), nullable=False, default='Paid') # Paid, Pending, Overdue
