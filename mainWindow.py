# sys pk
import sys
from numpy.random import rand as f_rand
from functools import partial
# third pk
from PyQt5 import QtWidgets, QtCore
import vtk, pclpy
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
# user pk
from VtkPointCloud import *
from Debug_Info_Widget import Debug_Info_Widget
from mySock import MySock

# Debug flags:
DebugFlag_Init_Points = False
DebugFlag_Init_Points_ReadFile = False  # null file
DebugFlag_Show_Info = False
DebugFlag_RoundMode = True

# Settings:
_ip = "169.254.104.114"
_port = 2111
_scan = "\x02sRN LMDscandata\x03"

Debug_Round_Period = 20  # (s)
Debug_Round_Gap = 0.02  # (s)

Debug_Round_Bottom = -0.5
Debug_Round_Top = 2.5
Debug_Round_anglemin = 0
Debug_Round_anglemax = 150


class MainWindow(QtWidgets.QMainWindow):
    Debug_info_widget_open = False
    refresh_signal = QtCore.pyqtSignal()
    Debug_Add_Info_signal = QtCore.pyqtSignal(str)
    later_process_signal = QtCore.pyqtSignal(int)
    def __init__(self):
        #
        super().__init__()
        # 先放置UI控件
        self.initUI()
        # 初始化VTK窗口
        self.initScreen()
        # 初始化网络接口
        self.initSock()

        # 按钮连接最后执行
        self.initFunc()

        # Debug

        if DebugFlag_Show_Info == True:
            self.Debug_Show_Info()

        # Show
        self.showMaximized()

    def initUI(self):
        # Create Widgets
        self.central_widget = QtWidgets.QWidget()
        self.main_layout1 = QtWidgets.QVBoxLayout()
        self.main_layout2 = QtWidgets.QHBoxLayout()
        self.top_panel = QtWidgets.QHBoxLayout()
        self.left_panel = QtWidgets.QVBoxLayout()
        self.right_panel = QtWidgets.QHBoxLayout()
        self.connect_btn = QtWidgets.QPushButton("connect")
        # self.default_login_btn = QtWidgets.QPushButton("default login")
        self.read_once_btn = QtWidgets.QPushButton("read once")
        self.read_always_btn = QtWidgets.QPushButton()
        self.Debug_info_btn = QtWidgets.QPushButton("Debug info window")
        self.qvtkinteract = QVTKRenderWindowInteractor()

        # Button Text
        # eg:
        self.read_always_btn.Text_Off = partial(self.read_always_btn.setText, "read always")
        self.read_always_btn.Text_On = partial(self.read_always_btn.setText, "stop read")
        self.read_always_btn.Text_Off()

        # set mainFrame UI
        self.setCentralWidget(self.central_widget)
        self.setGeometry(200, 100, 1000, 800)  # this is nonsense
        self.setWindowTitle("LMS511_Connector")
        self.central_widget.setLayout(self.main_layout1)
        self.main_layout1.addLayout(self.top_panel)
        self.main_layout1.addLayout(self.main_layout2)
        self.main_layout2.addLayout(self.left_panel)
        self.main_layout2.addLayout(self.right_panel)

        self.top_panel.addWidget(self.connect_btn)
        # self.buttonpanel.addWidget(self.defaultlogin)
        self.top_panel.addWidget(self.read_once_btn)
        self.top_panel.addWidget(self.read_always_btn)

        self.top_panel.addStretch(1)
        self.left_panel.addWidget(self.Debug_info_btn)

        #self.left_panel.addStretch(1)
        # points screen
        self.right_panel.addWidget(self.qvtkinteract)

        # status message
        self.statusBar().showMessage("unconnected")

    def initFunc(self):

        self.connect_btn.clicked.connect(self.mysock.connect)
        self.read_once_btn.clicked.connect(self.mysock.readonce)
        self.read_always_btn.clicked.connect(self.mysock.readalways)
        self.Debug_info_btn.clicked.connect(self.Debug_Show_Info)

        self.refresh_signal.connect(self.refresh_fun)
        self.Debug_Add_Info_signal.connect(self.Debug_Add_Info_fun)

    def initScreen(self):
        if DebugFlag_RoundMode == True:
            self.pointCloud = VtkPointCloud(zMin=Debug_Round_Bottom, zMax=Debug_Round_Top)
        else:
            self.pointCloud = VtkPointCloud()

        colors = vtk.vtkNamedColors()
        self.iren = self.qvtkinteract.GetRenderWindow().GetInteractor()
        #

        # display

        self.renderer = vtk.vtkRenderer()
        self.pointCloud.vtkActor.GetProperty().SetPointSize(3)
        self.renderer.AddActor(self.pointCloud.vtkActor)
        self.renderer.SetBackground(colors.GetColor3d('SlateGray'))

        # add central axis
        maxis = vtk.vtkAxisActor()
        # maxis.GetProperty().SetColor(0,1,0)
        # maxis.GetProperty().SetDiffuse(0.7)
        # maxis.GetProperty().SetSpecular(0.4)
        # maxis.GetProperty().SetSpecularPower(20)
        # transform = vtk.vtkTransform()
        # transform.Translate(5.0, 0.0, 0.0)
        # maxis.SetUserTransform(transform)

        maxis.SetPosition(0, 0, 0)
        # maxis.GetXAxisCaptionActor2D().GetCaptionTextProperty().SetColor(colors.GetColor3d("Red"))
        maxis.SetGridlineXLength(1)
        maxis.SetGridlineYLength(1)
        maxis.SetGridlineZLength(1)
        maxis.SetAxisType(0)
        # maxis.SetLabels(vtk.vtkStringArray("hello"))

        self.renderer.AddActor(maxis)
        #
        self.iren.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
        self.qvtkinteract.GetRenderWindow().AddRenderer(self.renderer)
        # Add axes here success!
        # Add axes
        axes_actor = vtk.vtkAnnotatedCubeActor()
        axes_actor.SetFaceTextScale(0.2)
        axes_actor.SetXPlusFaceText('Left')
        axes_actor.SetXMinusFaceText('Right')
        axes_actor.SetYMinusFaceText('Back')
        axes_actor.SetYPlusFaceText('Front')
        axes_actor.SetZMinusFaceText('Botton')
        axes_actor.SetZPlusFaceText('Top')
        axes_actor.GetTextEdgesProperty().SetColor(colors.GetColor3d("Green"))
        axes_actor.GetTextEdgesProperty().SetLineWidth(1)
        axes_actor.GetCubeProperty().SetColor(colors.GetColor3d("Blue"))
        # # this bug happened when widget defines not in 'self.' type
        #  maybe when function finished ,the widget released.
        self.axes = vtk.vtkOrientationMarkerWidget()
        self.axes.SetOrientationMarker(axes_actor)
        self.axes.SetInteractor(self.iren)
        self.axes.EnabledOn()
        self.axes.InteractiveOn()

        self.qvtkinteract.Initialize()

    def initSock(self):
        self.mysock = MySock(self)

    def process_once_data(self, data):
        points = data_process(data)
        self.pointCloud.setPoints(points)
        self.refresh()
        # self.qvtkinteract.GetRenderWindow().Render()

    def process_round_data(self, data, temp_time, total_times):
        if temp_time == 0:
            self.pointCloud.clearPoints()
        points = Debug_rounddata_process(data, temp_time, total_times)
        self.pointCloud.addPoints(points)
        self.refresh()

    def process_round_data2(self, data, now_in_period, period):

        points = Debug_rounddata_process(data, now_in_period, period)
        self.pointCloud.addPoints(points)
        self.refresh()

    def process_round_data_later(self, data, temp_time, total_times):

        if temp_time == 0:
            self.pointCloud.clearPoints()
            self.later_data = []
            #self.later_process_signal=QtCore.pyqtSignal(int)  # class attr
            self.later_process_signal.connect(self.process_round_data_final)

        self.later_data.append(data)

        if temp_time == total_times-1:
            self.later_process_signal.emit(total_times)


    def process_round_data_final(self,total_times):
        ii = 0
        for data in self.later_data:
            points = Debug_rounddata_process(data, ii, total_times)
            self.pointCloud.addPoints(points)
            self.refresh()
            ii = ii + 1

    # Debug
    # Add Points
    def Debug_initPoints(self):
        if DebugFlag_Init_Points_ReadFile == True:
            self._read = vtk.vtkPLYReader()
            self._read.SetFileName("teapot.ply")
            self._read.Update()
            self._poly_data = self._read.GetOutput()
            self._mapper = vtk.vtkPolyDataMapper()
            self._mapper.SetInputData(self._poly_data)
            self._mapper.SetColorModeToDefault()
            self._mapper.SetScalarRange(-10, 10)
            self._mapper.SetScalarVisibility(1)
            self._vtkActor = vtk.vtkActor()
            self._vtkActor.SetMapper(self._mapper)
            self.renderer.AddActor(self._vtkActor)
            self.renderer.Render()
        else:
            self.D_APBtn = QtWidgets.QPushButton("Add Point")
            self.buttonpanel.addWidget(self.D_APBtn)
            self.D_APBtn.clicked.connect(self.Debug_addPoints)

            for kkkk in range(1000):
                point = 20 * (f_rand(3) - 0.5)
                self.pointCloud.addPoint(point)
            for kkkk in range(10):
                self.pointCloud.addPoint(0.2 * (f_rand(3) - 0.5))

    def Debug_addPoints(self):
        point = 20 * (f_rand(3) - 0.5)
        self.pointCloud.addPoint(point)
        self.qvtkinteract.GetRenderWindow().Render()

    # Round Scan Mode
    def Debug_initRoundMode(self):
        self.RoundModeBtn = QtWidgets.QPushButton("Round Scan")
        self.left_panel.addWidget(self.RoundModeBtn)
        self.RoundModeBtn.clicked.connect(
            lambda :self.mysock.round_read(Debug_Round_Period,Debug_Round_Gap))

        self.angle_change_btn = QtWidgets.QPushButton("Change Angle Interval")
        self.left_panel.addWidget(self.angle_change_btn)
        self.angle_change_btn.clicked.connect(
            lambda: self.mysock.angle_interval(Debug_Round_anglemin, Debug_Round_anglemax))

    # Refresh Screen
    def refresh(self):
        self.refresh_signal.emit()

    def refresh_fun(self):
        self.qvtkinteract.GetRenderWindow().Render()

    # Window ,show information
    def Debug_Show_Info(self):
        if self.Debug_info_widget_open == False:
            self.Debug_info_widget = Debug_Info_Widget(self)
        else:
            self.Debug_info_widget.close()

    def Debug_Add_Info(self, s):
        try:
            self.Debug_Add_Info_signal.emit(s)
        except Exception as e:
            print(e)

    def Debug_Add_Info_fun(self, s):
        if self.Debug_info_widget_open:
            self.Debug_info_widget.textpanel.appendPlainText(s)



def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()

    # Debug
    if DebugFlag_Init_Points == True:
        window.Debug_initPoints()
    if DebugFlag_RoundMode == True:
        window.Debug_initRoundMode()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
