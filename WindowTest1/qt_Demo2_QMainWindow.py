import sys
from PyQt5 import QtWidgets

class mainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()


    def initUI(self):
        self.resize(800,600)

        widget=QtWidgets.QWidget(self)
        self.setCentralWidget(widget)

        exitAction = QtWidgets.QAction("Exit",self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(QtWidgets.qApp.quit)

        menu=self.menuBar()
        filemenu=menu.addMenu("&File")
        filemenu.addAction(exitAction)

        info=self.statusBar()
        info.showMessage("status...")

        tool=self.addToolBar("tools")
        tool.addAction(exitAction)

        mainLayout = QtWidgets.QHBoxLayout(widget)
        leftLayout=QtWidgets.QVBoxLayout()
        leftLayout.heightForWidth(100)
        mainLayout.addLayout(leftLayout)
        rightLayout = QtWidgets.QVBoxLayout()
        mainLayout.addLayout(rightLayout)
        button = QtWidgets.QPushButton("button1")
        leftLayout.addWidget(QtWidgets.QLabel("Hello "))
        leftLayout.addWidget(QtWidgets.QLabel("Input: "))
        leftLayout.addWidget(QtWidgets.QLineEdit(""))
        leftLayout.addStretch(1)
        leftLayout.addWidget(button)
        rightLayout.addWidget(QtWidgets.QPushButton("button2"))
        rightLayout.addStretch(1)

        self.show()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = mainWindow()
    sys.exit(app.exec_())
