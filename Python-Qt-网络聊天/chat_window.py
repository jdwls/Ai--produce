from PyQt5.QtWidgets import (QWidget, QTextEdit, QLineEdit, QVBoxLayout,
                            QPushButton, QListWidget, QLabel, QHBoxLayout,
                            QToolButton, QScrollArea)
from PyQt5.QtGui import QFont, QPixmap, QColor, QPainter
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
                background-color: #F5F5F5;
                font-family: 'Segoe UI', sans-serif;
            }
            QTextEdit {
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                padding: 8px;
                font-size: 14px;
                selection-background-color: #2196F3;
                selection-color: white;
            }
            QLineEdit {
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 20px;
                padding: 8px 16px;
                font-size: 14px;
                selection-background-color: #2196F3;
                selection-color: white;
            }
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 20px;
                padding: 8px 24px;
                font-size: 14px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #1565C0;
            }
            QListWidget {
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                padding: 4px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #F0F0F0;
            }
            QListWidget::item:hover {
                background-color: #F5F5F5;
            }
            QListWidget::item:selected {
                background-color: #2196F3;
                color: white;
            }
            QScrollBar:vertical {
                background: #F5F5F5;
                width: 10px;
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:vertical {
                background: #BDBDBD;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                background: none;
            }
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {
                background: none;
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
        # 加载默认头像
        try:
            avatar = QPixmap(":/images/default_avatar.png")
            if avatar.isNull():
                raise Exception("Default avatar not found")
        except:
            # 创建圆形灰色默认头像
            avatar = QPixmap(50, 50)
            avatar.fill(Qt.transparent)
            painter = QPainter(avatar)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setBrush(QColor("#CCCCCC"))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(0, 0, 50, 50)
            painter.end()
            
        self.avatarLabel.setPixmap(avatar.scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation))
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
                    <div style="text-align: right; margin: 8px;">
                        <div style="display: inline-block; max-width: 70%; 
                            background-color: #2196F3;
                            padding: 12px 16px;
                            border-radius: 12px;
                            margin-left: 30%;
                            box-shadow: 0 1px 3px rgba(0,0,0,0.12);
                            color: white;">
                            <div style="font-size: 12px; color: rgba(255,255,255,0.8);">{timestamp}</div>
                            <div style="margin-top: 4px;">{content}</div>
                        </div>
                    </div>
                    """
                else:
                    # 他人发送的消息
                    msg_html = f"""
                    <div style="margin: 8px;">
                        <div style="display: inline-block; max-width: 70%; 
                            background-color: white;
                            padding: 12px 16px;
                            border-radius: 12px;
                            margin-right: 30%;
                            box-shadow: 0 1px 3px rgba(0,0,0,0.12);">
                            <div style="font-size: 12px; color: #666;">{sender} · {timestamp}</div>
                            <div style="margin-top: 4px;">{content}</div>
                        </div>
                    </div>
                    """
                
                self.chatDisplay.append(msg_html)
                self.chatDisplay.verticalScrollBar().setValue(
                    self.chatDisplay.verticalScrollBar().maximum()
                )
        except:
            self.chatDisplay.append(message)
