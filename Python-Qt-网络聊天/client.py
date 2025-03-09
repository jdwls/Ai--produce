from PyQt5.QtWidgets import (QWidget, QTextEdit, QLineEdit, QVBoxLayout, QPushButton, 
                            QHBoxLayout, QStackedWidget, QListWidget, QLabel)
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QFont
import socket
import json
from users import Users

class LoginWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('登录')
        self.setGeometry(300, 300, 300, 200)
        
        layout = QVBoxLayout()
        
        # 用户名输入
        self.usernameInput = QLineEdit()
        self.usernameInput.setPlaceholderText('请输入用户名')
        
        # 登录按钮
        self.loginButton = QPushButton('登录')
        self.loginButton.clicked.connect(self.login)
        
        # 注册按钮
        self.registerButton = QPushButton('注册')
        self.registerButton.clicked.connect(self.register)
        
        layout.addWidget(QLabel('欢迎使用聊天室'))
        layout.addWidget(self.usernameInput)
        layout.addWidget(self.loginButton)
        layout.addWidget(self.registerButton)
        
        self.setLayout(layout)
        
    def login(self):
        username = self.usernameInput.text()
        if self.parent.users.login(username):
            self.parent.current_user = username
            self.parent.showChatWindow()
            self.parent.initSocket(username)
        else:
            self.usernameInput.setPlaceholderText('用户不存在')
            
    def register(self):
        username = self.usernameInput.text()
        if self.parent.users.register(username):
            self.usernameInput.setPlaceholderText('注册成功，请登录')
        else:
            self.usernameInput.setPlaceholderText('用户名已存在')

class ChatClient(QWidget):
    def __init__(self):
        super().__init__()
        self.users = Users()
        self.current_user = None
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('网络聊天室')
        self.setGeometry(300, 300, 800, 600)
        
        # 主布局
        mainLayout = QHBoxLayout()
        
        # 侧边栏
        self.sidebar = QWidget()
        sidebarLayout = QVBoxLayout()
        
        # 用户信息
        self.userInfo = QLabel('未登录')
        self.userInfo.setFont(QFont('Arial', 12))
        sidebarLayout.addWidget(self.userInfo)
        
        # 用户列表
        self.userList = QListWidget()
        sidebarLayout.addWidget(QLabel('在线用户'))
        sidebarLayout.addWidget(self.userList)
        
        self.sidebar.setLayout(sidebarLayout)
        
        # 主内容区域
        self.stackedWidget = QStackedWidget()
        
        # 登录界面
        self.loginWindow = LoginWindow(self)
        self.stackedWidget.addWidget(self.loginWindow)
        
        # 聊天界面
        self.chatWindow = QWidget()
        chatLayout = QVBoxLayout()
        
        self.chatDisplay = QTextEdit()
        self.chatDisplay.setReadOnly(True)
        
        self.messageInput = QLineEdit()
        self.messageInput.returnPressed.connect(self.sendMessage)
        
        self.sendButton = QPushButton('发送')
        self.sendButton.clicked.connect(self.sendMessage)
        
        chatLayout.addWidget(self.chatDisplay)
        chatLayout.addWidget(self.messageInput)
        chatLayout.addWidget(self.sendButton)
        
        self.chatWindow.setLayout(chatLayout)
        self.stackedWidget.addWidget(self.chatWindow)
        
        mainLayout.addWidget(self.sidebar, 1)
        mainLayout.addWidget(self.stackedWidget, 3)
        
        self.setLayout(mainLayout)
        self.showLoginWindow()
        
    def showLoginWindow(self):
        self.stackedWidget.setCurrentIndex(0)
        
    def showChatWindow(self):
        self.userInfo.setText(f'当前用户: {self.current_user}')
        self.stackedWidget.setCurrentIndex(1)
        
    def initSocket(self, username):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(('127.0.0.1', 12345))
        self.client_socket.send(username.encode('utf-8'))
        
        # 启动接收线程
        self.receive_thread = ReceiveThread(self.client_socket)
        self.receive_thread.received.connect(self.displayMessage)
        self.receive_thread.start()
        
    def sendMessage(self):
        message = self.messageInput.text()
        if message:
            self.client_socket.send(message.encode('utf-8'))
            self.messageInput.clear()
            
    def displayMessage(self, message):
        try:
            data = json.loads(message)
            if data.get('type') == 'userlist':
                self.userList.clear()
                for user in data['users']:
                    self.userList.addItem(user)
            else:
                self.chatDisplay.append(message)
        except:
            self.chatDisplay.append(message)
            
    def closeEvent(self, event):
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
