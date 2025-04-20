import json
import os

class Users:
    def __init__(self):
        self.users_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'json/users.json')
        if not os.path.exists(self.users_file):
            with open(self.users_file, 'w') as f:
                json.dump({}, f)

    def register(self, username, password):
        import hashlib
        
        try:
            with open(self.users_file, 'r') as f:
                users = json.load(f)
            
            if username in users:
                return False
                
            # Hash password using SHA-256
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            users[username] = {
                'status': 'offline',
                'password': password_hash
            }
            
            with open(self.users_file, 'w') as f:
                json.dump(users, f)
            return True
        except Exception as e:
            print(f"Registration error: {str(e)}")
            return False

    def login(self, username, password):
        import hashlib
        
        try:
            with open(self.users_file, 'r') as f:
                users = json.load(f)
                
            if username not in users:
                return False
                
            # Verify password hash
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            if users[username].get('password') != password_hash:
                return False
                
            users[username]['status'] = 'online'
            with open(self.users_file, 'w') as f:
                json.dump(users, f)
            return True
        except Exception as e:
            print(f"Login error: {str(e)}")
            return False

    def get_users(self):
        with open(self.users_file, 'r') as f:
            return json.load(f)
