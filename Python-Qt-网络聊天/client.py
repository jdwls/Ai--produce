from PyQt5.QtWidgets import (QWidget, QTextEdit, QLineEdit, QVBoxLayout, QPushButton)
from PyQt5.QtCore import QThread, pyqtSignal
import socket

class ChatClient(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.initSocket()
        
    def initUI(self):
        self.setWindowTitle('网络聊天室 - 客户端')
        self.setGeometry(300, 300, 400, 500)
        
        # 聊天显示区域
        self.chatDisplay = QTextEdit()
        self.chatDisplay.setReadOnly(True)
        
        # 消息输入框
        self.messageInput = QLineEdit()
        self.messageInput.returnPressed.connect(self.sendMessage)
        
        # 发送按钮
        self.sendButton = QPushButton('发送')
        self.sendButton.clicked.connect(self.sendMessage)
        
        # 布局
        layout = QVBoxLayout()
        layout.addWidget(self.chatDisplay)
        layout.addWidget(self.messageInput)
        layout.addWidget(self.sendButton)
        
        self.setLayout(layout)
        
    def initSocket(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(('127.0.0.1', 12345))
        
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
