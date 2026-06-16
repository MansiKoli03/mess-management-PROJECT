import os
from datetime import datetime, timedelta
from flask import Flask, render_template, redirect, url_for, request, flash, send_file
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import extract

from models import db, Admin, Customer, Attendance, Payment
from utils import export_db_to_excel, create_backup

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_super_secret_key_change_in_production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mess.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(admin_id):
    return Admin.query.get(int(admin_id))

# Initialize Database and Default Admin
with app.app_context():
    db.create_all()
    if not Admin.query.filter_by(username='admin').first():
        hashed_pw = generate_password_hash('password123', method='pbkdf2:sha256')
        default_admin = Admin(username='admin', password_hash=hashed_pw)
        db.session.add(default_admin)
        db.session.commit()

@app.before_request
def before_request():
    app.permanent_session_lifetime = timedelta(minutes=30)
    
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        admin = Admin.query.filter_by(username=username).first()
        
        if admin and check_password_hash(admin.password_hash, password):
            login_user(admin, remember=True)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
            
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    total_customers = Customer.query.count()
    active_customers = Customer.query.filter_by(status='Active').count()
    
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    paid_this_month = db.session.query(db.func.sum(Payment.amount)).filter(
        extract('month', Payment.payment_date) == current_month,
        extract('year', Payment.payment_date) == current_year,
        Payment.status == 'Paid'
    ).scalar() or 0
    
    # Calculate pending based on active customers fees minus payments this month
    total_expected = db.session.query(db.func.sum(Customer.monthly_fee)).filter_by(status='Active').scalar() or 0
    pending_payments = total_expected - paid_this_month
    
    today = datetime.now().date()
    todays_attendance = Attendance.query.filter_by(date=today, status='Present').count()
    
    return render_template('dashboard.html', 
                           total_customers=total_customers,
                           active_customers=active_customers,
                           paid_this_month=paid_this_month,
                           pending_payments=pending_payments,
                           todays_attendance=todays_attendance)

# --- CUSTOMER ROUTES ---
@app.route('/customers', methods=['GET', 'POST'])
@login_required
def customers():
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        mobile = request.form.get('mobile_number')
        alternate = request.form.get('alternate_number')
        address = request.form.get('address')
        joining = datetime.strptime(request.form.get('joining_date'), '%Y-%m-%d').date() if request.form.get('joining_date') else datetime.now().date()
        fee = float(request.form.get('monthly_fee', 0))
        due_date = int(request.form.get('payment_due_date', 1))
        status = request.form.get('status', 'Active')
        notes = request.form.get('notes')
        
        new_customer = Customer(full_name=full_name, mobile_number=mobile, alternate_number=alternate,
                                address=address, joining_date=joining, monthly_fee=fee, 
                                payment_due_date=due_date, status=status, notes=notes)
        db.session.add(new_customer)
        db.session.commit()
        export_db_to_excel(app)
        flash('Customer added successfully', 'success')
        return redirect(url_for('customers'))
        
    all_customers = Customer.query.all()
    return render_template('customers.html', customers=all_customers)

@app.route('/customer/edit/<int:id>', methods=['POST'])
@login_required
def edit_customer(id):
    customer = Customer.query.get_or_404(id)
    customer.full_name = request.form.get('full_name')
    customer.mobile_number = request.form.get('mobile_number')
    customer.alternate_number = request.form.get('alternate_number')
    customer.address = request.form.get('address')
    if request.form.get('joining_date'):
        customer.joining_date = datetime.strptime(request.form.get('joining_date'), '%Y-%m-%d').date()
    customer.monthly_fee = float(request.form.get('monthly_fee', 0))
    customer.payment_due_date = int(request.form.get('payment_due_date', 1))
    customer.status = request.form.get('status', 'Active')
    customer.notes = request.form.get('notes')
    
    db.session.commit()
    export_db_to_excel(app)
    flash('Customer updated successfully', 'success')
    return redirect(url_for('customers'))

@app.route('/customer/delete/<int:id>', methods=['POST'])
@login_required
def delete_customer(id):
    customer = Customer.query.get_or_404(id)
    db.session.delete(customer)
    db.session.commit()
    export_db_to_excel(app)
    flash('Customer deleted successfully', 'success')
    return redirect(url_for('customers'))

# --- ATTENDANCE ROUTES ---
@app.route('/attendance', methods=['GET', 'POST'])
@login_required
def attendance():
    today = datetime.now().date()
    date_str = request.args.get('date', today.strftime('%Y-%m-%d'))
    selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    
    active_customers = Customer.query.filter_by(status='Active').all()
    
    # Get attendance for selected date
    attendances = Attendance.query.filter_by(date=selected_date).all()
    att_dict = {a.customer_id: a.status for a in attendances}
    
    if request.method == 'POST':
        customer_id = int(request.form.get('customer_id'))
        status = request.form.get('status')
        
        att = Attendance.query.filter_by(customer_id=customer_id, date=selected_date).first()
        if att:
            att.status = status
        else:
            att = Attendance(customer_id=customer_id, date=selected_date, status=status)
            db.session.add(att)
            
        db.session.commit()
        export_db_to_excel(app)
        return {"success": True} # For AJAX
        
    return render_template('attendance.html', customers=active_customers, att_dict=att_dict, selected_date=selected_date)

# --- PAYMENTS ROUTES ---
@app.route('/payments', methods=['GET', 'POST'])
@login_required
def payments():
    if request.method == 'POST':
        customer_id = request.form.get('customer_id')
        amount = float(request.form.get('amount', 0))
        date = datetime.strptime(request.form.get('payment_date'), '%Y-%m-%d').date() if request.form.get('payment_date') else datetime.now().date()
        method = request.form.get('payment_method')
        status = request.form.get('status', 'Paid')
        
        payment = Payment(customer_id=customer_id, amount=amount, payment_date=date, payment_method=method, status=status)
        db.session.add(payment)
        db.session.commit()
        export_db_to_excel(app)
        flash('Payment recorded successfully', 'success')
        return redirect(url_for('payments'))
        
    all_payments = Payment.query.order_by(Payment.payment_date.desc()).all()
    active_customers = Customer.query.filter_by(status='Active').all()
    return render_template('payments.html', payments=all_payments, customers=active_customers)

# --- CONTACTS ROUTES ---
@app.route('/contacts')
@login_required
def contacts():
    all_customers = Customer.query.all()
    return render_template('contacts.html', customers=all_customers)

# --- REPORTS & BACKUP ROUTES ---
@app.route('/reports')
@login_required
def reports():
    return render_template('reports_backup.html')

@app.route('/backup')
@login_required
def backup():
    excel_path, sqlite_path = create_backup(app)
    flash(f'Backup created successfully.', 'success')
    return redirect(url_for('reports'))

@app.route('/download/excel')
@login_required
def download_excel():
    filepath = os.path.join(app.root_path, 'data', 'customers.xlsx')
    if not os.path.exists(filepath):
        export_db_to_excel(app)
    return send_file(filepath, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
