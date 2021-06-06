import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(200, 100, 1000, 800)  # this is nonsense
        self.setWindowTitle("LMS511_Connector")
        self.setWindowIcon(QIcon('lidar.ico'))
        self.setIconSize(QSize(20, 20))
        mainTab = QTabWidget()
        self.setCentralWidget(mainTab)
        tabControl = QWidget()
        mainTab.addTab(tabControl, "Controller")
        control_layout = QHBoxLayout()
        cleft_panel = QVBoxLayout()
        cright_panel = QVBoxLayout()
        tabControl.setLayout(control_layout)  # goes h
        control_layout.addLayout(cleft_panel)  # v
        control_layout.addLayout(cright_panel)  # v

        tabVisualization = QWidget()
        # visualization_layout = QVBoxLayout()
        # vtop_panel = QHBoxLayout()
        # vbottom_container = QHBoxLayout()
        # vleft_panel = QVBoxLayout()
        # vright_panel = QVBoxLayout()
        mainTab.addTab(tabVisualization, "Visualization")
        self.show()

def main():
    app = QApplication(sys.argv)
    a=MainWindow()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
