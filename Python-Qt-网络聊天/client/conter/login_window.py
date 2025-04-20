from PyQt5.QtWidgets import (QWidget, QLineEdit, QVBoxLayout, QPushButton, QStyle,
                            QHBoxLayout, QLabel, QMessageBox, QGridLayout,
                            QCheckBox, QFrame, QGraphicsDropShadowEffect,
                            QProgressBar)
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QPoint, QSize, pyqtProperty
from PyQt5.QtGui import (QFont, QColor, QPalette, QLinearGradient, QBrush, QIcon)
import json
import os
from .users import Users

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
    def __init__(self, chat_window):
        super().__init__()
        self.chat_window = chat_window
        self.chat_window.users = Users()
        self.gradients = [
            ['#ff6a00', '#ee0979'],  # 日出色
            ['#00c6ff', '#0072ff'],  # 海洋蓝
            ['#43cea2', '#185a9d'],  # 森林绿
        ]
        self._gradient_index = 0
        self.initUI()
        self.setWindowIcon(self.getBuiltinIcon('logo'))  # 使用内置图标

    def initUI(self):
        self.setWindowTitle('登录')
        self.setMinimumSize(500, 400)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowMaximizeButtonHint)

        # 动态背景渐变
        self.gradient_animation = QPropertyAnimation(self, b"gradient_index")
        self.setupBackground()

        # 主布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(0)

        # 玻璃效果卡片
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.98);
                border-radius: 16px;
                border: 1px solid rgba(255,255,255,0.3);
                min-width: 380px;
            }
        """)
        card.setGraphicsEffect(self.createShadow(12, 30))
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(40, 40, 40, 40)
        card_layout.setSpacing(25)

        # 标题部分
        header = QLabel('欢迎回来')
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                font-size: 28px;
                font-weight: 600;
                margin-bottom: 15px;
            }
        """)

        # 表单部分
        form_layout = QVBoxLayout()
        form_layout.setSpacing(20)

        # 用户名输入
        self.usernameInput = self.createInputField('用户名', 'person')
        # 密码输入
        self.passwordInput = self.createInputField('密码', 'lock', is_password=True)
        
        # 附加选项
        option_layout = QHBoxLayout()
        self.rememberCheck = QCheckBox('记住登录状态')
        self.rememberCheck.setStyleSheet("""
            QCheckBox {
                color: #7f8c8d;
                font-size: 13px;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 5px;
                border: 1px solid #bdc3c7;
            }
            QCheckBox::indicator:checked {
                background-color: #3498db;
                border-color: #3498db;
            }
        """)
        self.forgotLabel = QLabel('<a href="#" style="color:#3498db;text-decoration:none;">忘记密码？</a>')
        self.forgotLabel.linkActivated.connect(self.showForgotPassword)
        
        option_layout.addWidget(self.rememberCheck)
        option_layout.addStretch()
        option_layout.addWidget(self.forgotLabel)

        # 错误提示
        self.errorLabel = QLabel()
        self.errorLabel.setStyleSheet("""
            QLabel {
                color: #e74c3c;
                background-color: rgba(231,76,60,0.1);
                border-radius: 6px;
                padding: 10px;
                font-size: 13px;
                border: 1px solid rgba(231,76,60,0.2);
            }
        """)
        self.errorLabel.setVisible(False)

        # 按钮组
        button_layout = QVBoxLayout()
        button_layout.setSpacing(15)
        
        self.loginButton = self.createButton('登录', '#3498db', icon='login')
        self.loginButton.clicked.connect(self.login)
        button_layout.addWidget(self.loginButton)
        
        self.registerButton = self.createButton('注册', '#2ecc71', icon='add-user')
        self.registerButton.clicked.connect(self.register)
        button_layout.addWidget(self.registerButton)

        # 组装界面
        form_layout.addWidget(header)
        form_layout.addLayout(self.usernameInput)
        form_layout.addLayout(self.passwordInput)
        form_layout.addLayout(option_layout)
        form_layout.addWidget(self.errorLabel)
        form_layout.addLayout(button_layout)
        
        card_layout.addLayout(form_layout)
        main_layout.addWidget(card, 0, Qt.AlignCenter)
        self.setLayout(main_layout)

        # 加载保存的登录信息
        self.loadRememberedLogin()

    def createInputField(self, label, icon_name, is_password=False):
        layout = QVBoxLayout()
        layout.setSpacing(8)
        
        # 标签
        lbl = QLabel(label)
        lbl.setStyleSheet("""
            color: #34495e;
            font-size: 14px;
            font-weight: 500;
        """)
        
        # 输入容器
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background-color: rgba(236,240,241,0.5);
                border-radius: 8px;
                border: 2px solid rgba(189,195,199,0.3);
            }
            QFrame:hover {
                border-color: #3498db;
            }
        """)
        
        # 内部布局
        inner_layout = QHBoxLayout(container)
        inner_layout.setContentsMargins(12, 8, 12, 8)
        inner_layout.setSpacing(10)
        
        # 图标
        icon = QLabel()
        icon.setPixmap(self.getBuiltinIcon(icon_name).pixmap(24, 24))
        
        # 输入框
        lineEdit = QLineEdit()
        lineEdit.setStyleSheet("""
            QLineEdit {
                background: transparent;
                border: none;
                color: #2c3e50;
                font-size: 15px;
                padding: 4px 0;
                selection-background-color: #3498db;
            }
            QLineEdit::placeholder {
                color: #95a5a6;
            }
        """)
        if is_password:
            lineEdit.setEchoMode(QLineEdit.Password)
            lineEdit.setPlaceholderText('输入密码')
            # 添加显示密码按钮
            toggle_btn = QPushButton()
            toggle_btn.setCheckable(True)
            toggle_btn.setIcon(self.getBuiltinIcon('eye'))
            toggle_btn.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    border: none;
                    padding: 0;
                    min-width: 24px;
                }
            """)
            toggle_btn.toggled.connect(lambda state, le=lineEdit: 
                le.setEchoMode(QLineEdit.Normal if state else QLineEdit.Password))
            inner_layout.addWidget(toggle_btn)
        else:
            lineEdit.setPlaceholderText('输入用户名')

        inner_layout.insertWidget(0, icon)
        inner_layout.addWidget(lineEdit)
        
        layout.addWidget(lbl)
        layout.addWidget(container)
        
        return layout

    def getBuiltinIcon(self, icon_name):
        """Get built-in Qt icon for given name"""
        icons = {
            'person': QStyle.SP_DirIcon,
            'lock': QStyle.SP_DialogSaveButton,
            'eye': QStyle.SP_FileDialogDetailedView,
            'login': QStyle.SP_DialogOkButton,
            'add-user': QStyle.SP_FileDialogNewFolder,
            'logo': QStyle.SP_FileDialogStart,
            'eye': QStyle.SP_FileDialogDetailedView
        }
        return self.style().standardIcon(icons.get(icon_name, QStyle.SP_FileIcon))

    def createButton(self, text, color, icon=None):
        btn = QPushButton(text)
        btn.setMinimumHeight(45)
        btn.setCursor(Qt.PointingHandCursor)
        
        style = f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 15px;
                font-weight: 500;
                padding-left: {35 if icon else 20}px;
            }}
            QPushButton:hover {{
                background-color: {self.adjustColor(color, -20)};
            }}
            QPushButton:pressed {{
                background-color: {self.adjustColor(color, -30)};
            }}
            QPushButton:disabled {{
                background-color: #bdc3c7;
            }}
        """
        
        if icon:
            btn.setIcon(self.getBuiltinIcon(icon))
            btn.setIconSize(QSize(20, 20))
            btn.setStyleSheet(style + """
                QPushButton::icon {
                    margin-left: -10px;
                    margin-right: 8px;
                }
            """)
        else:
            btn.setStyleSheet(style)
        
        btn.setGraphicsEffect(self.createShadow(8, 15))
        return btn

    def adjustColor(self, color, delta):
        c = QColor(color)
        return c.lighter(100 + delta).name()

    def createShadow(self, radius=10, offset=5):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(radius)
        shadow.setColor(QColor(0, 0, 0, 50))
        shadow.setOffset(0, offset)
        return shadow

    def setupBackground(self):
        self.gradient_index = 0
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animateBackground)
        self.timer.start(5000)

    def animateBackground(self):
        self.gradient_animation.stop()
        self.gradient_animation.setDuration(2000)
        self.gradient_animation.setStartValue(self.gradient_index)
        self.gradient_index = (self.gradient_index + 1) % len(self.gradients)
        self.gradient_animation.setEndValue(self.gradient_index)
        self.gradient_animation.start()

    def getGradientIndex(self):
        return self.gradient_index

    def setGradientIndex(self, index):
        self._gradient_index = index
        colors = self.gradients[self._gradient_index]
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0, QColor(colors[0]))
        gradient.setColorAt(1, QColor(colors[1]))
        palette = self.palette()
        palette.setBrush(QPalette.Window, QBrush(gradient))
        self.setPalette(palette)

    def getGradientIndex(self):
        return self._gradient_index

    gradient_index = pyqtProperty(int, fget=getGradientIndex, fset=setGradientIndex)

    def showForgotPassword(self):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("忘记密码")
        msg.setText("请联系管理员重置密码")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def loadRememberedLogin(self):
        try:
            # Get the QLineEdit widgets from their containers
            username_edit = self.usernameInput.itemAt(1).widget().findChild(QLineEdit)
            password_edit = self.passwordInput.itemAt(1).widget().findChild(QLineEdit)
            
            if os.path.exists('client/json/login_info.json'):
                with open('client/json/login_info.json', 'r') as f:
                    data = json.load(f)
                    if data.get('remember'):
                        username_edit.setText(data.get('username', ''))
                        password_edit.setText(data.get('password', ''))
                        self.rememberCheck.setChecked(True)
        except Exception as e:
            print(f"加载登录信息错误: {str(e)}")

    def saveLoginInfo(self):
        try:
            os.makedirs('client/json', exist_ok=True)
            # Get the QLineEdit widgets from their containers
            username_edit = self.usernameInput.itemAt(1).widget().findChild(QLineEdit)
            password_edit = self.passwordInput.itemAt(1).widget().findChild(QLineEdit)
            
            data = {
                'username': username_edit.text(),
                'password': password_edit.text(),
                'remember': self.rememberCheck.isChecked()
            }
            with open('client/json/login_info.json', 'w') as f:
                json.dump(data, f)
        except Exception as e:
            print(f"保存登录信息错误: {str(e)}")

    def validateInputs(self):
        # Get the QLineEdit widgets from their containers
        username_edit = self.usernameInput.itemAt(1).widget().findChild(QLineEdit)
        password_edit = self.passwordInput.itemAt(1).widget().findChild(QLineEdit)
        
        username = username_edit.text().strip()
        password = password_edit.text().strip()
        
        self.errorLabel.setVisible(False)
        valid = True
        
        if not username:
            self.showError("用户名不能为空", self.usernameInput)
            valid = False
        if not password:
            self.showError("密码不能为空", self.passwordInput)
            valid = False
            
        return valid

    def showError(self, message, field=None, is_success=False):
        self.errorLabel.setText(message)
        self.errorLabel.setVisible(True)
        
        if is_success:
            self.errorLabel.setStyleSheet("""
                QLabel {
                    color: #27ae60;
                    background-color: rgba(39,174,96,0.1);
                    border-radius: 6px;
                    padding: 10px;
                    font-size: 13px;
                    border: 1px solid rgba(39,174,96,0.2);
                }
            """)
        else:
            self.errorLabel.setStyleSheet("""
                QLabel {
                    color: #e74c3c;
                    background-color: rgba(231,76,60,0.1);
                    border-radius: 6px;
                    padding: 10px;
                    font-size: 13px;
                    border: 1px solid rgba(231,76,60,0.2);
                }
            """)
            
        if field:
            # Get the container widget from the layout
            container = field.itemAt(1).widget()
            anim = QPropertyAnimation(container, b"pos")
            anim.setDuration(100)
            anim.setEasingCurve(QEasingCurve.OutQuad)
            original_pos = container.pos()
            anim.setKeyValueAt(0.5, original_pos + QPoint(5,0))
            anim.setEndValue(original_pos)
            anim.start()

    def login(self):
        if not self.validateInputs():
            return
        
        self.loginButton.setEnabled(False)
        self.loginButton.setText('登录中...')
        
        # 模拟网络延迟
        QTimer.singleShot(1500, self.processLogin)

    def processLogin(self):
        # Get the QLineEdit widgets from their containers
        username_edit = self.usernameInput.itemAt(1).widget().findChild(QLineEdit)
        password_edit = self.passwordInput.itemAt(1).widget().findChild(QLineEdit)
        
        username = username_edit.text()
        password = password_edit.text()
        
        if self.chat_window.users.login(username, password):
            self.saveLoginInfo()
            # 登录成功动画
            self.chat_window.showChatWindow()
            self.close()
        else:
            self.showError("用户名或密码错误")
            self.loginButton.setEnabled(True)
            self.loginButton.setText('立即登录')


    def register(self):
        if not self.validateInputs():
            return
            
        self.registerButton.setEnabled(False)
        self.registerButton.setText('注册中...')
        
        # 模拟网络延迟
        QTimer.singleShot(1500, self.processRegister)

    def processRegister(self):
        # Get the QLineEdit widgets from their containers
        username_edit = self.usernameInput.itemAt(1).widget().findChild(QLineEdit)
        password_edit = self.passwordInput.itemAt(1).widget().findChild(QLineEdit)
        
        username = username_edit.text()
        password = password_edit.text()
        
        if self.chat_window.users.register(username, password):
            self.showError("注册成功！", is_success=True)
            # 自动填充登录表单
            username_edit.setText(username)
            password_edit.setText(password)
            self.rememberCheck.setChecked(True)
        else:
            self.showError("用户名已存在")
            
        self.registerButton.setEnabled(True)
        self.registerButton.setText('注册')

if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # 统一跨平台样式
    
    # 设置默认字体
    font = QFont()
    font.setFamily('Microsoft YaHei')
    font.setPointSize(10)
    app.setFont(font)
    
    window = LoginWindow()
    window.show()
    sys.exit(app.exec_())
