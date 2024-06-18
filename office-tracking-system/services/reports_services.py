def fetch_report_data():
    # Simulate data fetching for reports
    return {
        'user_activity': [
            {'user': 'John Doe', 'activity': 'Logged in', 'time': '2024-06-18 08:00'},
            {'user': 'Jane Smith', 'activity': 'Logged out', 'time': '2024-06-18 17:00'}
        ],
        'system_usage': [
            {'date': '2024-06-18', 'usage': '80%'},
            {'date': '2024-06-17', 'usage': '75%'}
        ]
    }
    
def fetch_occurrences_data():
    # This function would typically interact with a database to gather occurrence log data
    return [
        {'id': 1, 'date': '2024-06-18', 'time': '09:00 AM', 'user': 'John Doe', 'type': 'Entry'},
        {'id': 2, 'date': '2024-06-18', 'time': '05:00 PM', 'user': 'John Doe', 'type': 'Exit'}
    ]
