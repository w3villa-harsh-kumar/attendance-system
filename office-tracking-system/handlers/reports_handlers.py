import pandas as pd
from flask import render_template, request, redirect, url_for, session, Response
from flask_weasyprint import HTML, render_pdf
from services.reports_services import fetch_report_data


def download_pdf():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    # Fetch data for the report
    data = fetch_report_data()  # This should return HTML content
    html = render_template('reports.html', data=data)
    return render_pdf(HTML(string=html))

def download_csv():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    # Fetch or prepare your data as a DataFrame
    df = pd.DataFrame({
        'User': ['John Doe', 'Jane Smith'],
        'Activity': ['Logged in', 'Logged out'],
        'Time': ['2024-06-18 08:00', '2024-06-18 17:00']
    })
    csv = df.to_csv(index=False)
    return Response(
        csv,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=report.csv"}
    )
