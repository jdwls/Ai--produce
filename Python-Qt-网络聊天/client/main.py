import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from PyQt5.QtWidgets import QApplication
from client.conter.client import ChatClient

if __name__ == '__main__':
    app = QApplication(sys.argv)
    client = ChatClient()
    sys.exit(app.exec_())
