from PyQt5.QtWidgets import (QWidget, QStackedWidget, QHBoxLayout, 
                            QVBoxLayout, QLabel, QListWidget)
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QFont
import socket
import json
from .users import Users
from .login_window import LoginWindow
from .chat_window import ChatWindow

class ChatClient(QWidget):
    def __init__(self):
        super().__init__()
        self.users = Users()
        self.current_user = None
        self.initUI()
        
    def initUI(self):
        # 初始化登录和聊天窗口
        
        # 登录界面
        self.loginWindow = LoginWindow(self)
        self.loginWindow.show()
        
        # 聊天界面
        self.chatWindow = ChatWindow(self)
        
    def showChatWindow(self):
        self.loginWindow.close()
        self.chatWindow.setCurrentUser(self.current_user)
        self.chatWindow.show()
        
    def initSocket(self, username):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(('127.0.0.1', 12345))
        self.client_socket.send(username.encode('utf-8'))
        
        # 启动接收线程
        self.receive_thread = ReceiveThread(self.client_socket)
        self.receive_thread.received.connect(self.displayMessage)
        self.receive_thread.start()
        
    def displayMessage(self, message):
        self.chatWindow.displayMessage(message)
        
    def sendMessage(self, message):
        if hasattr(self, 'client_socket'):
            try:
                self.client_socket.send(message.encode('utf-8'))
            except:
                print("消息发送失败")
            
    def closeEvent(self, event):
        if hasattr(self, 'client_socket'):
            self.client_socket.close()
        event.accept()

class ReceiveThread(QThread):
    received = pyqtSignal(str)
    
    def __init__(self, socket):
        super().__init__()
        self.socket = socket
        
    def run(self):
        while True:
            try:
                message = self.socket.recv(1024).decode('utf-8')
                if message:
                    self.received.emit(message)
            except:
                break
