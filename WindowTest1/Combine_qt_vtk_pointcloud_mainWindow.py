import numpy
import sys
from PyQt5 import (QtWidgets, QtCore)
import vtk
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
import pclpy



class mainWindow(QtWidgets.QWidget):
    def __init__(self):
        #
        super().__init__()
        self.setGeometry(300,300,800,600)
        self.setWindowTitle("LMS511_Connector")


        mainlayout=QtWidgets.QBoxLayout(QtWidgets.QBoxLayout.LeftToRight,self)
        self.btn=QtWidgets.QPushButton("hello",self)
        self.btn.setFixedWidth(100)
        self.btn.clicked.connect(self.addPoints)

        mainlayout.addWidget(self.btn)
        self.qvtkinteract = QVTKRenderWindowInteractor(self)
        mainlayout.addWidget(self.qvtkinteract)


        #data
        self.pointCloud=VtkPointCloud()
        self.initPoints()


        #display
        self.renderer = vtk.vtkRenderer()
        self.renderer.AddActor(self.pointCloud.vtkActor)
        self.qvtkinteract.GetRenderWindow().AddRenderer(self.renderer)
        self.qvtkinteract.Initialize()











        #PCLVisualizer
        # self.myPointCloud = pclpy.pcl.PointCloud.PointXYZ()
        # pclpy.pcl.io.loadPLYFile('teapot.ply', self.myPointCloud)
        # self.pclviewer = pclpy.pcl.visualization.PCLVisualizer('Point Cloud viewer')
        # self.pclviewer.addPointCloud(self.myPointCloud)





        #Show
        self.show()

    def initPoints(self):
        for kkkk in range(10):
            point = 20 * (numpy.random.rand(3) - 0.5)
            self.pointCloud.addPoint(point)
        for kkkk in range(10):
            self.pointCloud.addPoint([0, 0, 0])

    def addPoints(self):
        point = 20 * (numpy.random.rand(3) - 0.5)
        self.pointCloud.addPoint(point)
        self.refresh()


    def refresh(self):
        self.renderer.AddActor(self.pointCloud.vtkActor)
        self.qvtkinteract.GetRenderWindow().AddRenderer(self.renderer)
        self.qvtkinteract.Initialize()


class VtkPointCloud:

    def __init__(self, zMin=-10.0, zMax=10.0, maxNumPoints=1e6):
        self.maxNumPoints = maxNumPoints
        self.vtkPolyData = vtk.vtkPolyData()
        self.clearPoints()
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(self.vtkPolyData)
        mapper.SetColorModeToDefault()
        mapper.SetScalarRange(zMin, zMax)
        mapper.SetScalarVisibility(1)
        self.vtkActor = vtk.vtkActor()
        self.vtkActor.SetMapper(mapper)

    def addPoint(self, point):
        if isinstance(point,list):
            pass
        if self.vtkPoints.GetNumberOfPoints() < self.maxNumPoints:
            pointId = self.vtkPoints.InsertNextPoint(point[:])
            self.vtkDepth.InsertNextValue(point[2])
            self.vtkCells.InsertNextCell(1)
            self.vtkCells.InsertCellPoint(pointId)
        else:
            r = numpy.random.randint(0, self.maxNumPoints)
            self.vtkPoints.SetPoint(r, point[:])
        self.vtkCells.Modified()
        self.vtkPoints.Modified()
        self.vtkDepth.Modified()

    def clearPoints(self):
        self.vtkPoints = vtk.vtkPoints()
        self.vtkCells = vtk.vtkCellArray()
        self.vtkDepth = vtk.vtkDoubleArray()
        self.vtkDepth.SetName('DepthArray')
        self.vtkPolyData.SetPoints(self.vtkPoints)
        self.vtkPolyData.SetVerts(self.vtkCells)
        self.vtkPolyData.GetPointData().SetScalars(self.vtkDepth)
        self.vtkPolyData.GetPointData().SetActiveScalars('DepthArray')






























if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = mainWindow()
    #window.iren.Initialize()  # Need this line to actually show the render inside Qt
    sys.exit(app.exec_())
