from PyQt5 import QtWidgets
from PyQt5 import QtCore


class InformationWindow(QtWidgets.QWidget):
    headText = "Debug information:"
    isShow = False
    appendSignal = QtCore.pyqtSignal(str)

    def __init__(self, master=None):
        super().__init__(master)
        # 设置总体布局
        self.resize(600, 400)
        self.move(1000, 100)
        self.setWindowTitle(self.headText)
        # 添加控件
        self.mainLayout = QtWidgets.QVBoxLayout(self)
        self.buttonPanel = QtWidgets.QHBoxLayout(self)
        self.textPanel = QtWidgets.QPlainTextEdit(self.headText, self)
        self.clearButton = QtWidgets.QPushButton("clear")

        self.mainLayout.addWidget(self.textPanel)
        self.mainLayout.addLayout(self.buttonPanel)
        self.buttonPanel.addStretch(1)
        self.buttonPanel.addWidget(self.clearButton)

        # 功能设置
        self.appendSignal.connect(self.append_fun)

        # 修改窗口及控件的功能
        self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)
        self.textPanel.setReadOnly(True)
        self.textPanel.setMaximumBlockCount(1000)
        self.clearButton.clicked.connect(self.clear)
        self.textPanel.setLineWrapMode(QtWidgets.QPlainTextEdit.NoWrap)

    def append(self, s):
        try:
            if self.isShow:
                self.appendSignal.emit(s)
        except Exception as e:
            print(e)

    def append_fun(self, s):
        try:
            if self.isShow:
                self.textPanel.appendPlainText(s)
        except Exception as e:
            print(e)

    def warning(self, s):
        if not self.isShow:
            self.show()
        self.append(s)

    def show(self):
        super().show()
        self.clear()
        self.isShow = True

    def clear(self):
        self.textPanel.clear()
        self.textPanel.setPlainText(self.headText)

    def closeEvent(self, event):
        # 点击窗口关闭按钮触发closeEvent
        # 或, 调用close()函数也会触发closeEvent
        # 要统一执行退出过程,请使用closeEvent而不是close
        self.clear()
        self.isShow = False
        self.hide()
