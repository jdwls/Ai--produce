from PyQt5.QtWidgets import (QWidget, QTextEdit, QLineEdit, QVBoxLayout,
                            QPushButton, QListWidget, QLabel, QHBoxLayout,
                            QToolButton, QScrollArea)
from PyQt5.QtGui import QFont, QPixmap, QColor
from PyQt5.QtCore import Qt
import json

class ChatWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.current_user = None
        self.initUI()

    def setCurrentUser(self, username):
        self.current_user = username
        self.userInfo.setText(f'当前用户: {username}')
        
    def initUI(self):
        self.setWindowTitle('网络聊天室')
        self.setGeometry(300, 300, 1000, 700)
        self.setStyleSheet("""
            QWidget {
                background-color: #F0F0F0;
            }
            QTextEdit {
                background-color: white;
                border: 1px solid #CCCCCC;
                border-radius: 5px;
                padding: 5px;
            }
            QLineEdit {
                background-color: white;
                border: 1px solid #CCCCCC;
                border-radius: 15px;
                padding: 5px 10px;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 15px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QListWidget {
                background-color: white;
                border: 1px solid #CCCCCC;
                border-radius: 5px;
            }
        """)
        
        # 主布局
        mainLayout = QHBoxLayout()
        mainLayout.setContentsMargins(5, 5, 5, 5)
        mainLayout.setSpacing(5)
        
        # 侧边栏
        self.sidebar = QWidget()
        sidebarLayout = QVBoxLayout()
        sidebarLayout.setContentsMargins(5, 5, 5, 5)
        sidebarLayout.setSpacing(10)
        
        # 用户信息
        userInfoLayout = QHBoxLayout()
        self.avatarLabel = QLabel()
        self.avatarLabel.setPixmap(QPixmap(":/images/default_avatar.png").scaled(50, 50, Qt.KeepAspectRatio))
        userInfoLayout.addWidget(self.avatarLabel)
        
        self.userInfo = QLabel('未登录')
        self.userInfo.setFont(QFont('Arial', 12, QFont.Bold))
        userInfoLayout.addWidget(self.userInfo)
        sidebarLayout.addLayout(userInfoLayout)
        
        # 用户列表
        sidebarLayout.addWidget(QLabel('在线用户'))
        self.userList = QListWidget()
        self.userList.setStyleSheet("""
            QListWidget::item {
                padding: 5px;
            }
            QListWidget::item:hover {
                background-color: #E0E0E0;
            }
        """)
        sidebarLayout.addWidget(self.userList)
        
        self.sidebar.setLayout(sidebarLayout)
        
        # 聊天区域
        chatLayout = QVBoxLayout()
        chatLayout.setContentsMargins(5, 5, 5, 5)
        chatLayout.setSpacing(5)
        
        # 聊天显示区域
        self.chatDisplay = QTextEdit()
        self.chatDisplay.setReadOnly(True)
        self.chatDisplay.setStyleSheet("""
            QTextEdit {
                font-size: 14px;
            }
        """)
        
        # 输入区域
        inputLayout = QHBoxLayout()
        inputLayout.setSpacing(5)
        
        # 表情按钮
        self.emojiButton = QToolButton()
        self.emojiButton.setText("😊")
        self.emojiButton.setStyleSheet("""
            QToolButton {
                font-size: 18px;
                padding: 5px;
                border: none;
            }
            QToolButton:hover {
                background-color: #E0E0E0;
                border-radius: 5px;
            }
        """)
        inputLayout.addWidget(self.emojiButton)
        
        self.messageInput = QLineEdit()
        self.messageInput.setPlaceholderText("输入消息...")
        self.messageInput.returnPressed.connect(self.sendMessage)
        inputLayout.addWidget(self.messageInput, 1)
        
        self.sendButton = QPushButton('发送')
        self.sendButton.clicked.connect(self.sendMessage)
        inputLayout.addWidget(self.sendButton)
        
        # 添加组件到主布局
        chatLayout.addWidget(self.chatDisplay, 1)
        chatLayout.addLayout(inputLayout)
        
        mainLayout.addWidget(self.sidebar, 1)
        mainLayout.addLayout(chatLayout, 3)
        
        self.setLayout(mainLayout)
        
    def sendMessage(self):
        if not hasattr(self.parent, 'client_socket'):
            return
            
        message = self.messageInput.text()
        if message:
            try:
                self.parent.client_socket.send(message.encode('utf-8'))
                self.messageInput.clear()
            except:
                self.chatDisplay.append('发送失败，请检查网络连接')
            
    def displayMessage(self, message):
        try:
            data = json.loads(message)
            if data.get('type') == 'userlist':
                self.userList.clear()
                for user in data['users']:
                    self.userList.addItem(user)
            else:
                # 格式化消息显示
                timestamp = data.get('timestamp', '')
                sender = data.get('sender', '未知用户')
                content = data.get('content', '')
                
                # 消息气泡样式
                if sender == self.current_user:
                    # 自己发送的消息
                    msg_html = f"""
                    <div style="text-align: right; margin: 5px;">
                        <div style="display: inline-block; max-width: 70%; 
                            background-color: #dcf8c6; 
                            padding: 8px 12px;
                            border-radius: 10px;
                            margin-left: 30%;">
                            <div style="font-size: 12px; color: #666;">{timestamp}</div>
                            <div>{content}</div>
                        </div>
                    </div>
                    """
                else:
                    # 他人发送的消息
                    msg_html = f"""
                    <div style="margin: 5px;">
                        <div style="display: inline-block; max-width: 70%; 
                            background-color: white; 
                            padding: 8px 12px;
                            border-radius: 10px;
                            margin-right: 30%;">
                            <div style="font-size: 12px; color: #666;">{sender} · {timestamp}</div>
                            <div>{content}</div>
                        </div>
                    </div>
                    """
                
                self.chatDisplay.append(msg_html)
                self.chatDisplay.verticalScrollBar().setValue(
                    self.chatDisplay.verticalScrollBar().maximum()
                )
        except:
            self.chatDisplay.append(message)
