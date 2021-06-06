import vtk, pclpy

def pcl_func():
    # PCLVisualizer
    myPointCloud = pclpy.pcl.PointCloud.PointXYZ()
    pclpy.pcl.io.loadPLYFile('teapot.ply', myPointCloud)
    pclviewer = pclpy.pcl.visualization.PCLVisualizer('Point Cloud viewer')
    pclviewer.addPointCloud(myPointCloud)




if __name__ == '__main__':

    pcl_func()