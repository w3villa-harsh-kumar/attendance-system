from controllers.auth_controller import login, dashboard, logout, user_management
from controllers.reports_controller import reports, occurrences_log
from handlers.reports_handlers import download_csv, download_pdf
from controllers.system_controller import system_settings

def init_routes(app):
    app.add_url_rule('/', 'login', login, methods=['GET', 'POST'])
    app.add_url_rule('/dashboard', 'dashboard', dashboard)
    app.add_url_rule('/logout', 'logout', logout)
    app.add_url_rule('/reports', 'reports', reports)
    app.add_url_rule('/download-pdf', 'download_pdf', download_pdf)
    app.add_url_rule('/download-csv', 'download_csv', download_csv)
    app.add_url_rule('/occurrences', 'occurrences_log', occurrences_log)
    app.add_url_rule('/user-management', 'user_management', user_management, methods=['GET', 'POST'])
    app.add_url_rule('/system-settings', 'system_settings', system_settings, methods=['GET', 'POST'])