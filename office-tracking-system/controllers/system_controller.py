from flask import flash, session, redirect, url_for, render_template, request
from services.system_services import fetch_system_settings, update_system_settings

def system_settings():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        settings_data = {key: value for key, value in request.form.items()}
        update_system_settings(settings_data)
        flash('Settings updated successfully', 'success')
        return redirect(url_for('system_settings'))

    settings = fetch_system_settings()
    return render_template('system_settings.html', settings=settings)
