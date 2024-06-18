from flask import render_template, request, redirect, session, url_for
from services.user_service import fetch_users, add_user, update_user, delete_user

def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'pass123':
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    attendances = [
        {'name': 'John Doe', 'time_in': '08:00 AM', 'time_out': '05:00 PM', 'status': 'Present'},
        {'name': 'Jane Smith', 'time_in': '09:00 AM', 'time_out': '05:00 PM', 'status': 'Present'}
    ]

    # You would typically fetch this data from your database
    return render_template('dashboard.html', attendances=attendances)

def logout():
    session.pop('logged_in', None)  # Clear the session
    return redirect(url_for('login'))

def user_management():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    users = fetch_users()
    if request.method == 'POST':
        if 'delete' in request.form:
            delete_user(request.form['delete'])
        elif 'update' in request.form:
            user_id = request.form['update']
            user_data = { 'name': request.form['name'], 'role': request.form['role'] }
            update_user(user_id, user_data)
        else:
            user_data = { 'name': request.form['name'], 'role': request.form['role'] }
            add_user(user_data)
        
        return redirect(url_for('user_management'))

    return render_template('user_management.html', users=users)