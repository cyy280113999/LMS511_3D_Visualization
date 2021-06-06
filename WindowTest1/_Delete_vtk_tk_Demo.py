

import tkinter
import vtk
#this sentence fix the error "no mudules 'vtkCommonCore'"
import sys
sys.path.append('D:\\Users\\HP\\miniconda3\\envs\\py36\\Lib\\site-packages\\vtk')
sys.path.append('D:\\Users\\HP\\miniconda3\\envs\\py36\\Lib\\site-packages\\vtk\\tk')
#
from vtk.tk.vtkTkRenderWindowInteractor import vtkTkRenderWindowInteractor


#import pclpy

mainWindow=tkinter.Tk()
mainWindow.title("mainW")
frame=tkinter.Frame(mainWindow).pack(fill=tkinter.BOTH,expand=1)


#viewer=pclpy.pcl.visualization.PCLVisualizer('Point Cloud viewer')



#RW
#1
#RenderWindow=viewer.getRenderWindow()
#2
render = vtk.vtkRenderer()
render.SetBackground(0.329412, 0.34902, 0.427451)
render.ResetCameraClippingRange()
# Setup for rendering window
RenderWindow = vtk.vtkRenderWindow()
RenderWindow.AddRenderer(render)

#
renWinInteractor = vtkTkRenderWindowInteractor(mainWindow,rw=RenderWindow,width=400,height=400)
renWinInteractor.Initialize()
renWinInteractor.pack(fill='both',expand=1)
renWinInteractor.Start()

RenderWindow.Render()

#

mainWindow.mainloop()
#while(not viewer.wasStopped()):
#    viewer.spinOnce(100)
