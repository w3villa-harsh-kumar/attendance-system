from flask import render_template, session, redirect, url_for
from services.reports_services import fetch_report_data, fetch_occurrences_data

def reports():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    data = fetch_report_data()
    return render_template('reports.html', data=data)

def occurrences_log():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    occurrences = fetch_occurrences_data()
    return render_template('occurrences_log.html', occurrences=occurrences)