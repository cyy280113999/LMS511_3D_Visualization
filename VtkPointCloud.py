import math
from numpy.random import randint
import vtk, pclpy

def data_process(data):
    # data process
    data = data.split(' ')
    if not data[0] == "\x02sRA":
        return []
    if data[-1].endswith('\x03'):
        data[-1] = data[-1][:-1]
    # 回波系数，乘数

    if data[21] == '40000000':
        factors = 2
    elif data[21] == '3F800000':
        factors = 1
    else:
        return []
    # 起始角度
    startangle = int(data[23], 16) / 10000
    # 角度分辨率
    anglestep = int(data[24], 16) / 10000
    # 测量得数据总量
    datanum = int(data[25], 16)
    points = []
    for i in range(datanum):
        point = []
        #                 radius     ,      unit:mm , double or not         angle factor    ,          degree to arc
        point.append(int(data[26 + i], 16) / 1000 * factors * math.cos((startangle + i * anglestep) / 180 * math.pi))
        point.append(int(data[26 + i], 16) / 1000 * factors * math.sin((startangle + i * anglestep) / 180 * math.pi))
        point.append(0)
        points.append(point)
    return points


def Debug_rounddata_process(data, temp_time, total_times=200):
    # left lay down
    data = data.split(' ')
    if not data[0] == "\x02sRA":
        print('error data')
        return []
    if data[-1].endswith('\x03'):
        data[-1] = data[-1][:-1]
    if data[21] == '40000000':
        factors = 2
    elif data[21] == '3F800000':
        factors = 1
    else:
        print('error data')
        return []

    startangle = int(data[23], 16) / 10000
    anglestep = int(data[24], 16) / 10000
    datanum = int(data[25], 16)
    points = []

    phi = temp_time / total_times * 2 * math.pi
    for i in range(datanum):
        try:
            point = []
            radius = int(data[26 + i], 16) / 1000 * factors
            theta = (startangle + i * anglestep) / 180 * math.pi
            point.append(radius * math.sin(theta) * math.cos(phi))  # X
            point.append(radius * math.sin(theta) * math.sin(phi))  # Y
            point.append(radius * math.cos(theta))  # Z
            points.append(point)
        except Exception as e:
            print("exception:",e)
            print("at time:%d, data num: %d, in [%d]" % (temp_time, datanum, i))
    return points


def pcl_func(self):
    # PCLVisualizer
    self.myPointCloud = pclpy.pcl.PointCloud.PointXYZ()
    pclpy.pcl.io.loadPLYFile('teapot.ply', self.myPointCloud)
    self.pclviewer = pclpy.pcl.visualization.PCLVisualizer('Point Cloud viewer')
    self.pclviewer.addPointCloud(self.myPointCloud)


class VtkPointCloud:

    def __init__(self, zMin=-10.0, zMax=10.0, maxNumPoints=1e6):
        self.maxNumPoints = maxNumPoints
        self.vtkPolyData = vtk.vtkPolyData()
        self.clearPoints()
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(self.vtkPolyData)
        vlut = PointColor2()  #color      #mapper.SetColorModeToDefault()
        mapper.SetLookupTable(vlut)
        mapper.SetScalarRange(zMin, zMax)
        mapper.SetScalarVisibility(1)
        self.vtkActor = vtk.vtkActor()
        self.vtkActor.SetMapper(mapper)

    def addPoint(self, point):
        if self.vtkPoints.GetNumberOfPoints() < self.maxNumPoints:
            pointId = self.vtkPoints.InsertNextPoint(point[:])
            self.vtkDepth.InsertNextValue(point[2])
            self.vtkCells.InsertNextCell(1)
            self.vtkCells.InsertCellPoint(pointId)
        else:
            r = randint(0, self.maxNumPoints)
            self.vtkPoints.SetPoint(r, point[:])
        self.vtkCells.Modified()
        self.vtkPoints.Modified()
        self.vtkDepth.Modified()

    def addPoints(self, points):
        if not points:
            return
        for point in points:
            self.addPoint(point)

    def setPoints(self,points):
        self.clearPoints()
        self.addPoints(points)

    def clearPoints(self):
        self.vtkPoints = vtk.vtkPoints()
        self.vtkCells = vtk.vtkCellArray()
        self.vtkDepth = vtk.vtkDoubleArray()
        self.vtkDepth.SetName('DepthArray')
        self.vtkPolyData.SetPoints(self.vtkPoints)
        self.vtkPolyData.SetVerts(self.vtkCells)
        self.vtkPolyData.GetPointData().SetScalars(self.vtkDepth)
        self.vtkPolyData.GetPointData().SetActiveScalars('DepthArray')




def PointColor():
    vlut = vtk.vtkLookupTable()
    vlut.SetNumberOfColors(10)
    a=0.5;b=0.7;c=1.0
    vlut.SetTableValue(0,  (b,a,a,c))
    vlut.SetTableValue(1,  (c,a,a,c))
    vlut.SetTableValue(2,  (c,b,a,c))
    vlut.SetTableValue(3,  (b,b,a,c))
    vlut.SetTableValue(4,  (b,c,a,c))
    vlut.SetTableValue(5,  (a,c,a,c))
    vlut.SetTableValue(6,  (a,c,b,c))
    vlut.SetTableValue(7,  (a,c,c,c))
    vlut.SetTableValue(8,  (a,b,c,c))
    vlut.SetTableValue(9,  (a,a,c,c))
    #vlut.SetTableValue(10, (c,a,b,c))
    #vlut.SetTableValue(11, (a,b,b,c))
    #vlut.SetTableValue(12, (b,b,b,c))
    #vlut.SetTableValue(13, (c,b,b,c))
    #vlut.SetTableValue(14, (a,c,b,c))
    #vlut.SetTableValue(15, (b,c,b,c))
    vlut.Build()
    return vlut

def PointColor2():
    vlut = vtk.vtkLookupTable()
    vlut.SetHueRange(0.83, 0)
    vlut.SetAlphaRange(1, 1)
    vlut.SetValueRange(1, 1)
    vlut.SetSaturationRange(1, 1)
    vlut.SetNumberOfTableValues(256)
    vlut.Build()
    return vlut

