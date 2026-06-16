import os
import shutil
from datetime import datetime
import pandas as pd
from openpyxl import Workbook
from models import db, Customer, Attendance, Payment

def export_db_to_excel(app):
    with app.app_context():
        # Fetch data
        customers = Customer.query.all()
        attendances = Attendance.query.all()
        payments = Payment.query.all()
        
        # Convert to DataFrame
        df_customers = pd.DataFrame([{
            'Customer_ID': c.id,
            'Name': c.full_name,
            'Mobile': c.mobile_number,
            'Alternate_Mobile': c.alternate_number,
            'Address': c.address,
            'Joining_Date': c.joining_date.strftime('%Y-%m-%d') if c.joining_date else '',
            'Monthly_Fee': c.monthly_fee,
            'Due_Date': c.payment_due_date,
            'Status': c.status,
            'Notes': c.notes
        } for c in customers])
        
        df_attendances = pd.DataFrame([{
            'Date': a.date.strftime('%Y-%m-%d'),
            'Customer_ID': a.customer_id,
            'Customer_Name': a.customer.full_name if a.customer else '',
            'Attendance_Status': a.status
        } for a in attendances])
        
        df_payments = pd.DataFrame([{
            'Date': p.payment_date.strftime('%Y-%m-%d'),
            'Customer_ID': p.customer_id,
            'Customer_Name': p.customer.full_name if p.customer else '',
            'Amount': p.amount,
            'Payment_Method': p.payment_method,
            'Status': p.status
        } for p in payments])
        
        # Save to excel
        filepath = os.path.join(app.root_path, 'data', 'customers.xlsx')
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            if df_customers.empty:
                pd.DataFrame(columns=['Customer_ID', 'Name', 'Mobile', 'Alternate_Mobile', 'Address', 'Joining_Date', 'Monthly_Fee', 'Due_Date', 'Status', 'Notes']).to_excel(writer, sheet_name='Customers', index=False)
            else:
                df_customers.to_excel(writer, sheet_name='Customers', index=False)
                
            if df_attendances.empty:
                pd.DataFrame(columns=['Date', 'Customer_ID', 'Customer_Name', 'Attendance_Status']).to_excel(writer, sheet_name='Attendance', index=False)
            else:
                df_attendances.to_excel(writer, sheet_name='Attendance', index=False)
                
            if df_payments.empty:
                pd.DataFrame(columns=['Date', 'Customer_ID', 'Customer_Name', 'Amount', 'Payment_Method', 'Status']).to_excel(writer, sheet_name='Payments', index=False)
            else:
                df_payments.to_excel(writer, sheet_name='Payments', index=False)

def create_backup(app):
    export_db_to_excel(app)
    excel_path = os.path.join(app.root_path, 'data', 'customers.xlsx')
    sqlite_path = os.path.join(app.root_path, 'instance', 'mess.db')
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = os.path.join(app.root_path, 'backups')
    os.makedirs(backup_dir, exist_ok=True)
    
    backup_excel = os.path.join(backup_dir, f'customers_backup_{timestamp}.xlsx')
    backup_sqlite = os.path.join(backup_dir, f'mess_backup_{timestamp}.db')
    
    if os.path.exists(excel_path):
        shutil.copy2(excel_path, backup_excel)
    if os.path.exists(sqlite_path):
        shutil.copy2(sqlite_path, backup_sqlite)
    
    return backup_excel, backup_sqlite
