#use py3.6

import pclpy
from pclpy import pcl

pc=pclpy.pcl.PointCloud.PointXYZ()
#pcl.io.loadPCDFile('bunny.pcd',pc)
pcl.io.loadPLYFile('teapot.ply',pc)



viewer=pcl.visualization.PCLVisualizer('Point Cloud viewer')
viewer.addPointCloud(pc)
while(not viewer.wasStopped()):
    viewer.spinOnce(100)

