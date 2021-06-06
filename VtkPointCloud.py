import math
import vtk


def data_process(data):
    # data process
    # raw_data = data
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
    if datanum == 0:
        return
    points = []
    for i in range(datanum):
        try:
            point = []
            #                 radius     ,      unit:mm , double or not         angle factor    ,          degree to arc
            point.append(
                int(data[26 + i], 16) / 1000 * factors * math.cos((startangle + i * anglestep) / 180 * math.pi))
            point.append(
                int(data[26 + i], 16) / 1000 * factors * math.sin((startangle + i * anglestep) / 180 * math.pi))
            point.append(0)
            points.append(point)
        except Exception as e:
            print("exception:", e)
            print('i = %d ' % (i) + 'datanum: %d ' % (datanum))
            # print('the raw data is : ' + raw_data)
    return points


def Debug_rounddata_process(data, now_in_period, period):
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

    phi = now_in_period / period * 2 * math.pi
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
            print("exception:", e)
            print("at time:%d, data num: %d, in [%d]" % (now_in_period, datanum, i))
            # print('the raw data is : ' + raw_data)
            print('i = %d ' % (i) + 'datanum: %d ' % (datanum))
    return points


class VtkPointCloud:
    # 访问vtkActor获得数据
    def __init__(self, zMin=-10.0, zMax=10.0, maxNumPoints=1e7):
        self.maxNumPoints = maxNumPoints
        self.zMin = zMin
        self.zMax = zMax

        self.vtkPoints = vtk.vtkPoints()
        self.vtkCells = vtk.vtkCellArray()
        self.vtkDepth = vtk.vtkDoubleArray()
        self.vtkDepth.SetName('DepthArray')
        self.vtkPolyData = vtk.vtkPolyData()
        self.mapper = vtk.vtkPolyDataMapper()
        self.vtkActor = vtk.vtkActor()

        self.vtkPolyData.SetPoints(self.vtkPoints)
        self.vtkPolyData.SetVerts(self.vtkCells)
        self.vtkPolyData.GetPointData().SetScalars(self.vtkDepth)
        self.vtkPolyData.GetPointData().SetActiveScalars('DepthArray')

        self.mapper.SetInputData(self.vtkPolyData)
        self.vtkActor.SetMapper(self.mapper)

        self.clearPoints()  # link points & poly & mapper
        self.mapperColorSet()

    # get data in types
    def getActor(self):
        return self.vtkActor

    # 用不同的 polydata 显示不同的数据
    def setOutPoly(self, polydata: vtk.vtkPolyData):
        # # use addpoint, correctly
        # self.clearPoints()
        # points = polydata.GetPoints()
        # for i in range(points.GetNumberOfPoints()):
        #     point = points.GetPoint(i)
        #     self.addPoint(point)

        # rebuild polydata, correctly
        self.vtkPolyData = polydata
        self.vtkPoints = self.vtkPolyData.GetPoints()
        self.vtkCells = vtk.vtkCellArray()
        self.vtkDepth = vtk.vtkDoubleArray()
        self.vtkDepth.SetName('DepthArray')
        for i in range(self.vtkPoints.GetNumberOfPoints()):
            point = self.vtkPoints.GetPoint(i)
            self.vtkDepth.InsertNextValue(point[2])
            self.vtkCells.InsertNextCell(1)
            self.vtkCells.InsertCellPoint(i)
        self.vtkPoints.Modified()
        self.vtkCells.Modified()
        self.vtkDepth.Modified()
        self.vtkPolyData.SetVerts(self.vtkCells)
        self.vtkPolyData.GetPointData().SetScalars(self.vtkDepth)
        self.vtkPolyData.GetPointData().SetActiveScalars('DepthArray')
        self.mapper.SetInputData(self.vtkPolyData)
        self.mapperColorSet()  # 不起作用

        # # remove color , white points
        # # this change place which the mapper point to
        # _filter = vtk.vtkVertexGlyphFilter()
        # _filter.AddInputData(polydata)
        # self.mapper.SetInputConnection(_filter.GetOutputPort())
    # import vtk
    # filename = 'teapot.ply'
    # reader = vtk.vtkPLYReader()
    # reader.SetFileName(filename)
    # reader.Update()
    # polydata = reader.GetOutput()
    # points = polydata.GetPoints()
    # point = points.GetPoint(1)
    def getPoly(self):
        return self.vtkPolyData

    def getMapper(self):
        return self.mapper

    def setPointSize(self, n):
        if n >= 1 & n <= 10:
            self.vtkActor.GetProperty().SetPointSize(n)

    def mapperColorSet(self):
        self.vlut = PointColor2()  # color      #self.mapper.SetColorModeToDefault()
        self.mapper.SetLookupTable(self.vlut)
        self.mapper.SetScalarRange(self.zMin, self.zMax)
        self.mapper.SetScalarVisibility(1)

    def setColorRange(self, zMin, zMax):
        self.zMin = zMin
        self.zMax = zMax
        self.mapper.SetScalarRange(zMin, zMax)

    def addPoint(self, point):
        if self.vtkPoints.GetNumberOfPoints() < self.maxNumPoints:
            pointId = self.vtkPoints.InsertNextPoint(point[:])
            self.vtkDepth.InsertNextValue(point[2])
            self.vtkCells.InsertNextCell(1)
            self.vtkCells.InsertCellPoint(pointId)
        else:
            print('no space for point to add!')
        self.vtkCells.Modified()
        self.vtkPoints.Modified()
        self.vtkDepth.Modified()

    def addPoints(self, points):
        if not points:
            return
        for point in points:
            self.addPoint(point)

    def setPoints(self, points):
        self.clearPoints()
        self.addPoints(points)

    def clearPoints(self):
        # recreate points cells depth , and add into polydata
        self.vtkPoints = vtk.vtkPoints()
        self.vtkCells = vtk.vtkCellArray()
        self.vtkDepth = vtk.vtkDoubleArray()
        self.vtkDepth.SetName('DepthArray')
        self.vtkPolyData.SetPoints(self.vtkPoints)
        self.vtkPolyData.SetVerts(self.vtkCells)
        self.vtkPolyData.GetPointData().SetScalars(self.vtkDepth)
        self.vtkPolyData.GetPointData().SetActiveScalars('DepthArray')
        self.mapper.SetInputData(self.vtkPolyData)


def PointColor():
    vlut = vtk.vtkLookupTable()
    vlut.SetNumberOfColors(10)
    a = 0.5
    b = 0.7
    c = 1.0
    vlut.SetTableValue(0, (b, a, a, c))
    vlut.SetTableValue(1, (c, a, a, c))
    vlut.SetTableValue(2, (c, b, a, c))
    vlut.SetTableValue(3, (b, b, a, c))
    vlut.SetTableValue(4, (b, c, a, c))
    vlut.SetTableValue(5, (a, c, a, c))
    vlut.SetTableValue(6, (a, c, b, c))
    vlut.SetTableValue(7, (a, c, c, c))
    vlut.SetTableValue(8, (a, b, c, c))
    vlut.SetTableValue(9, (a, a, c, c))
    # vlut.SetTableValue(10, (c,a,b,c))
    # vlut.SetTableValue(11, (a,b,b,c))
    # vlut.SetTableValue(12, (b,b,b,c))
    # vlut.SetTableValue(13, (c,b,b,c))
    # vlut.SetTableValue(14, (a,c,b,c))
    # vlut.SetTableValue(15, (b,c,b,c))
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


def get_program_parameters(s):
    import argparse
    description = 'Generate image data, then write a .ply file.'
    epilogue = '''
   '''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue)
    parser.add_argument('filename', help='A required ply filename.', nargs='?',
                        const=s,
                        type=str, default=s)
    args = parser.parse_args()
    return args.filename
