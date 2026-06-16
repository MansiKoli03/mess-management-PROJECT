# Mess Management System

A fully functional, modern, responsive web application for managing a food mess business. 
Built using Python Flask, SQLite, and vanilla HTML/CSS/JS.

## Features

- **Secure Login System**: Session-based authentication for admin users.
- **Dashboard**: High-level statistics and charts for Total/Active Customers, Payments, and Attendance.
- **Customer Management**: Add, edit, delete, and search customers.
- **Attendance Tracking**: Mark daily attendance (Present, Absent, Late).
- **Payment Management**: Record payments and track pending balances.
- **Contacts**: Quick access to call or WhatsApp customers directly from the browser.
- **Automated Data Sync**: SQLite data is automatically exported to Excel sheets (`data/customers.xlsx`) on every modification.
- **Backups**: Create timestamped backups of the SQLite database and Excel files with a single click.
- **Dark/Light Mode**: Toggleable theme for a better viewing experience.

## Setup Instructions

### Prerequisites
- Python 3.8+ installed on Windows.

### Installation

1. **Open a Terminal / Command Prompt** in this project folder.
2. **(Optional but recommended)** Create and activate a virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```
3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Run the Application**:
   ```bash
   python app.py
   ```
5. **Access the App**: Open your web browser and go to `http://127.0.0.1:5000/`.

### Default Credentials
On the first run, the database is automatically created along with a default admin user.
- **Username**: `admin`
- **Password**: `password123`

> Note: For production use, it is highly recommended to change the default password in `app.py` or implement an admin profile management feature.

## Technical Details
- **Backend**: Flask
- **Database**: SQLite (`instance/mess.db`)
- **Data Export**: `openpyxl` & `pandas` (`data/customers.xlsx`)
- **Frontend**: HTML5, CSS3 (Custom Variables), Vanilla JavaScript, Chart.js.
