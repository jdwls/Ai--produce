import json
import os

class Users:
    def __init__(self):
        self.users_file = os.path.join(os.path.dirname(__file__), 'users.json')
        if not os.path.exists(self.users_file):
            with open(self.users_file, 'w') as f:
                json.dump({}, f)

    def register(self, username):
        with open(self.users_file, 'r') as f:
            users = json.load(f)
        
        if username in users:
            return False
            
        users[username] = {'status': 'offline'}
        with open(self.users_file, 'w') as f:
            json.dump(users, f)
        return True

    def login(self, username):
        with open(self.users_file, 'r') as f:
            users = json.load(f)
            
        if username not in users:
            return False
            
        users[username]['status'] = 'online'
        with open(self.users_file, 'w') as f:
            json.dump(users, f)
        return True

    def get_users(self):
        with open(self.users_file, 'r') as f:
            return json.load(f)
