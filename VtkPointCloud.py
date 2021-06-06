import vtk


class VtkPointCloud:
    # 访问vtkActor获得数据
    def __init__(self, zMin=-10.0, zMax=10.0, maxNumPoints=1e8):
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
    def setOutPoly(self, polydata: vtk.vtkPolyData, *, colorOn=True):
        # # use addpoint, correctly
        # self.clearPoints()
        # points = polydata.GetPoints()
        # for i in range(points.GetNumberOfPoints()):
        #     point = points.GetPoint(i)
        #     self.addPoint(point)

        # rebuild polydata, correctly
        if colorOn == True:
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
        else:
            # remove color , white points
            # this change place which the mapper point to
            _filter = vtk.vtkVertexGlyphFilter()
            _filter.AddInputData(polydata)
            self.mapper.SetInputConnection(_filter.GetOutputPort())

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
        if zMin >= zMax:
            return
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
