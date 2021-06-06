import sys
from PyQt5.QtWidgets import QWidget, QApplication


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = QWidget()
    w.show()
    w.setWindowTitle("Hello PyQt5")
    sys.exit(app.exec_())