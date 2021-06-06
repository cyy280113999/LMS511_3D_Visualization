import vtk

cube=vtk.vtkCubeSource()
cube.Update()

cube_mapper=vtk.vtkPolyDataMapper()
cube_mapper.SetInputData(cube.GetOutput())

cube_actor=vtk.vtkActor()
cube_actor.SetMapper(cube_mapper)

cube_actor.GetProperty().SetColor(1.0,0.0,0.0)

renderer=vtk.vtkRenderer()
renderer.SetBackground(0.0, 0.0, 0.0)#背景只有一个所以是Set()
renderer.AddActor(cube_actor)#因为actor有可能为多个所以是add()

render_window = vtk.vtkRenderWindow()
render_window.SetWindowName("My First Cube")
render_window.SetSize(400,400)
render_window.AddRenderer(renderer)# 渲染也会有可能有多个渲染把他们一起显示

interactor = vtk.vtkRenderWindowInteractor()
interactor.SetRenderWindow(render_window)
interactor.Initialize()
render_window.Render()
interactor.Start()