# Simulated data store and functions for demonstration
users_db = [
    {'id': 1, 'name': 'John Doe', 'role': 'Employee'},
    {'id': 2, 'name': 'Jane Smith', 'role': 'Manager'}
]

def fetch_users():
    return users_db

def add_user(user_data):
    new_id = len(users_db) + 1
    user_data['id'] = new_id
    users_db.append(user_data)
    return user_data

def update_user(user_id, update_data):
    for user in users_db:
        if user['id'] == user_id:
            user.update(update_data)
            return user
    return None

def delete_user(user_id):
    global users_db
    users_db = [user for user in users_db if user['id'] != user_id]
    return True
