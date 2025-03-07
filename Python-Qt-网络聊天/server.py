import socket
import threading

class ChatServer:
    def __init__(self):
        self.clients = []
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('0.0.0.0', 12345))
        self.server_socket.listen(5)
        print("服务器已启动，等待客户端连接...")
        
    def start(self):
        while True:
            client_socket, addr = self.server_socket.accept()
            print(f"新客户端连接：{addr}")
            self.clients.append(client_socket)
            threading.Thread(target=self.handle_client, args=(client_socket,)).start()
            
    def handle_client(self, client_socket):
        while True:
            try:
                message = client_socket.recv(1024)
                if not message:
                    break
                self.broadcast(message, client_socket)
            except:
                break
                
        self.clients.remove(client_socket)
        client_socket.close()
        print(f"客户端断开连接")
        
    def broadcast(self, message, sender_socket):
        for client in self.clients:
            if client != sender_socket:
                try:
                    client.send(message)
                except:
                    client.close()
                    self.clients.remove(client)

if __name__ == '__main__':
    server = ChatServer()
    server.start()
