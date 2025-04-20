import sys
import os
# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
from PyQt5.QtWidgets import QApplication
from client.conter.client import ChatClient

if __name__ == '__main__':
    app = QApplication(sys.argv)
    client = ChatClient()
    sys.exit(app.exec_())
