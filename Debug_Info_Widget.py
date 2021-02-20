from PyQt5 import QtWidgets
from PyQt5 import QtCore
class Debug_Info_Widget(QtWidgets.QWidget):
    message=[]

    def __init__(self,master):
        super().__init__()
        # 设置总体布局
        self.resize(600,800)
        self.move(1000,100)
        # 添加控件
        self.mainlayout=QtWidgets.QVBoxLayout(self)
        self.buttonPanel=QtWidgets.QHBoxLayout(self)
        self.textpanel = QtWidgets.QPlainTextEdit("Debug information:",self)
        self.clrbtn = QtWidgets.QPushButton("clear")

        self.mainlayout.addWidget(self.textpanel)
        self.mainlayout.addLayout(self.buttonPanel)
        self.buttonPanel.addStretch(1)
        self.buttonPanel.addWidget(self.clrbtn)

        # 修改窗口及控件的功能
        self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)
        self.textpanel.setReadOnly(True)
        self.textpanel.setMaximumBlockCount(1000)
        self.clrbtn.clicked.connect(self.myclear)
        self.textpanel.setLineWrapMode(QtWidgets.QPlainTextEdit.NoWrap)

        # 通知主体, 窗口已打开
        self.master = master
        self.master.Debug_info_widget_open = True
        # 显示
        self.show()

    # def append(self,s):
    #
    #     self.textpanel.setText(self.message)
    def myclear(self):
        self.textpanel.clear()
        self.textpanel.appendPlainText("Debug information:")

    def closeEvent(self, event):
        # 点击窗口关闭按钮触发closeEvent
        # 或, 调用close()函数也会触发closeEvent
        # 要统一执行退出过程,请使用closeEvent而不是close
        self.master.Debug_info_widget_open = False
        event.accept()
