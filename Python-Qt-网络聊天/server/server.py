import socket
import threading
import json
import os

class ChatServer:
    def __init__(self):
        self.clients = {}  # {username: socket}
        self.users_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'json/server_users.json')
        if not os.path.exists(self.users_file):
            with open(self.users_file, 'w') as f:
                json.dump({}, f)
                
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('0.0.0.0', 12345))
        self.server_socket.listen(5)
        print("服务器已启动，等待客户端连接...")
        
    def start(self):
        while True:
            client_socket, addr = self.server_socket.accept()
            print(f"新客户端连接：{addr}")
            threading.Thread(target=self.handle_client, args=(client_socket,)).start()
            
    def handle_client(self, client_socket):
        username = None
        try:
            # 接收用户名
            username = client_socket.recv(1024).decode('utf-8')
            if username in self.clients:
                client_socket.send('用户名已存在'.encode('utf-8'))
                client_socket.close()
                return
                
            self.clients[username] = client_socket
            self.update_user_status(username, 'online')
            self.broadcast_userlist()
            
            while True:
                message = client_socket.recv(1024)
                if not message:
                    break
                self.broadcast_message(f"{username}: {message.decode('utf-8')}")
                
        except Exception as e:
            print(f"客户端错误: {e}")
        finally:
            if username:
                self.clients.pop(username, None)
                self.update_user_status(username, 'offline')
                self.broadcast_userlist()
            client_socket.close()
            print(f"客户端断开连接")
            
    def update_user_status(self, username, status):
        with open(self.users_file, 'r') as f:
            users = json.load(f)
        users[username] = {'status': status}
        with open(self.users_file, 'w') as f:
            json.dump(users, f)
            
    def broadcast_message(self, message):
        import datetime
        msg_data = {
            'type': 'message',
            'timestamp': datetime.datetime.now().strftime('%H:%M'),
            'content': message
        }
        for client in self.clients.values():
            try:
                client.send(json.dumps(msg_data).encode('utf-8'))
            except:
                continue
                
    def broadcast_userlist(self):
        userlist = json.dumps({
            'type': 'userlist',
            'users': list(self.clients.keys())
        })
        self.broadcast_message(userlist)

if __name__ == '__main__':
    server = ChatServer()
    server.start()
