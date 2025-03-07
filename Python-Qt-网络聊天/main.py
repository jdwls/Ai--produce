import sys
from PyQt5.QtWidgets import QApplication
from client import ChatClient

if __name__ == '__main__':
    app = QApplication(sys.argv)
    client = ChatClient()
    client.show()
    sys.exit(app.exec_())
