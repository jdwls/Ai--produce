from PyQt5.QtWidgets import (QWidget, QLineEdit, QVBoxLayout, QPushButton, 
                            QHBoxLayout, QLabel, QMessageBox, QGridLayout,
                            QCheckBox, QFrame, QGraphicsDropShadowEffect)
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont, QColor, QPalette
import json


class MockUserManager:
    def __init__(self):
        self.users = {}

    def login(self, username, password):
        return username in self.users and self.users[username] == password

    def register(self, username, password):
        if username in self.users:
            return False
        self.users[username] = password
        return True


class LoginWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.parent.users = MockUserManager()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('登录')
        self.setGeometry(300, 300, 400, 300)

        # 设置主背景颜色
        palette = self.palette()
        palette.setColor(QPalette.Background, QColor('#f5f5f5'))
        self.setPalette(palette)

        # 主布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(0)

        # 卡片容器
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                padding: 20px;
            }
        """)
        card.setGraphicsEffect(self.createShadow())

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(20)

        # 标题
        title = QLabel('欢迎登录')
        title.setFont(QFont('Arial', 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #333;")

        # 使用垂直布局
        form_layout = QVBoxLayout()
        form_layout.setSpacing(20)
        form_layout.setContentsMargins(0, 0, 0, 0)

        # 用户名输入框
        username_layout = QHBoxLayout()
        username_label = QLabel('用户名：')
        self.usernameInput = QLineEdit()
        self.usernameInput.setPlaceholderText('用户名')
        self.setupInputField(self.usernameInput)
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.usernameInput)
        form_layout.addLayout(username_layout)

        # 密码输入框
        password_layout = QHBoxLayout()
        password_label = QLabel('密码：')
        self.passwordInput = QLineEdit()
        self.passwordInput.setPlaceholderText('密码')
        self.passwordInput.setEchoMode(QLineEdit.Password)
        self.setupInputField(self.passwordInput)
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.passwordInput)
        form_layout.addLayout(password_layout)

        # 记住密码
        self.rememberCheck = QCheckBox('记住密码')
        self.rememberCheck.setStyleSheet("""
            QCheckBox {
                color: #666;
                font-size: 13px;
                margin-left: 0.5em;
            }
        """)
        form_layout.addWidget(self.rememberCheck, 0, Qt.AlignLeft)

        # 按钮布局
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)

        self.loginButton = self.createButton('登录', '#2196F3')
        self.loginButton.clicked.connect(self.login)

        self.registerButton = self.createButton('注册', '#4CAF50')
        self.registerButton.clicked.connect(self.register)

        button_layout.addWidget(self.loginButton)
        button_layout.addWidget(self.registerButton)

        # 添加组件到卡片布局
        card_layout.addWidget(title)
        card_layout.addLayout(form_layout)
        card_layout.addLayout(button_layout)

        # 添加卡片到主布局
        main_layout.addWidget(card)

        self.setLayout(main_layout)

        # 加载记住的登录信息
        self.loadRememberedLogin()

    def createShadow(self):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 50))
        shadow.setOffset(0, 3)
        return shadow

    def createButton(self, text, color):
        btn = QPushButton(text)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px;
                font-size: 14px;
                min-width: 100px;
            }}
            QPushButton:hover {{
                background-color: {self.darkenColor(color)};
            }}
        """)
        return btn

    def darkenColor(self, color):
        # 将颜色变暗15%
        c = QColor(color)
        return c.darker(115).name()

    def setupInputField(self, field):
        field.setStyleSheet("""
            QLineEdit {
                background-color: transparent;
                border: none;
                border-bottom: 2px solid #ddd;
                padding: 8px 0;
                font-size: 14px;
                min-width: 150px;
            }
            QLineEdit:focus {
                border-bottom: 2px solid #2196F3;
            }
        """)

        # 添加输入框动画
        self.anim = QPropertyAnimation(field, b"geometry")
        self.anim.setDuration(200)
        self.anim.setEasingCurve(QEasingCurve.OutQuad)

        field.focusInEvent = lambda event: self.animateInput(field, True)
        field.focusOutEvent = lambda event: self.animateInput(field, False)

    def animateInput(self, field, focus):
        rect = field.geometry()
        if focus:
            self.anim.setStartValue(rect)
            self.anim.setEndValue(rect.adjusted(0, 0, 0, 5))
        else:
            self.anim.setStartValue(rect)
            self.anim.setEndValue(rect.adjusted(0, 0, 0, -5))
        self.anim.start()

    def loadRememberedLogin(self):
        try:
            with open('json/login_info.json', 'r') as f:
                data = json.load(f)
                if data.get('remember'):
                    self.usernameInput.setText(data.get('username', ''))
                    self.passwordInput.setText(data.get('password', ''))
                    self.rememberCheck.setChecked(True)
        except FileNotFoundError:
            pass

    def saveLoginInfo(self):
        if self.rememberCheck.isChecked():
            data = {
                'username': self.usernameInput.text(),
                'password': self.passwordInput.text(),
                'remember': True
            }
            with open('json/login_info.json', 'w') as f:
                json.dump(data, f)
        else:
            try:
                import os
                os.remove('json/login_info.json')
            except:
                pass

    def login(self):
        username = self.usernameInput.text()
        password = self.passwordInput.text()

        if not username or not password:
            QMessageBox.warning(self, '错误', '用户名和密码不能为空')
            return

        # 显示加载动画
        self.loginButton.setText('登录中...')
        self.loginButton.setEnabled(False)
        QTimer.singleShot(1000, lambda: self.completeLogin(username, password))

    def completeLogin(self, username, password):
        if self.parent.users.login(username, password):
            self.saveLoginInfo()
            self.parent.current_user = username
            # 显示聊天窗口
            try:
                self.parent.showChatWindow()
                self.parent.initSocket(username)
                self.close()
            except Exception as e:
                print(f"窗口切换错误: {str(e)}")
                QMessageBox.critical(self, '错误', '无法显示聊天窗口')
                self.loginButton.setText('登录')
                self.loginButton.setEnabled(True)
        else:
            QMessageBox.warning(self, '错误', '用户名或密码错误')
            self.loginButton.setText('登录')
            self.loginButton.setEnabled(True)

    def register(self):
        username = self.usernameInput.text()
        password = self.passwordInput.text()

        if not username or not password:
            QMessageBox.warning(self, '错误', '用户名和密码不能为空')
            return

        if self.parent.users.register(username, password):
            QMessageBox.information(self, '成功', '注册成功，请登录')
        else:
            QMessageBox.warning(self, '错误', '用户名已存在')


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    parent = QWidget()
    login_window = LoginWindow(parent)
    login_window.show()
    sys.exit(app.exec_())
    login_window.show()
    sys.exit(app.exec_())
