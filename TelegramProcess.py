import numpy as np
import math

TelegramList = ['Command Type', 'Command', 'Version Number', 'Device Number', 'Serial Number',
                'Device Status 1 00=OK', 'Device Status 2 00=OK', 'Telegram Counter',
                'Scan Counter', 'Time Since Start Up', 'Time of Transmission', 'Stats of Digital Input 1',
                'Stats of Digital Input2', 'Status of Digital Output 1', 'Status of Digital Output 2',
                'Reserved', 'Scan Frequency', 'Mesurement Frequency', 'Encoder Position', 'Encoder Speed',
                'Content', 'Scale Factor', 'Scale Factor Offset', 'Start Angle', 'Steps', 'Amount of Data',
                'Data']  # data
SubTgList = TelegramList[20:]  # telegram used
TelDict = {}


# data process with sRA
def data_process(dataB):
    dataB = dataB[1:-1]
    dataStr = dataB.decode('ascii')
    datas = dataStr.split(' ')
    if not datas[0] == "sRA":
        return []

    ContentIndex = datas.index('DIST1')
    for index, comment in zip(range(len(SubTgList)), SubTgList):
        TelDict[comment] = ContentIndex + index
    # 回波系数，乘数
    factorHex = datas[TelDict['Scale Factor']]
    if factorHex == '40000000':
        factors = 2
    elif factorHex == '3F800000':
        factors = 1
    else:
        return []
    index2num = lambda _: int(datas[_], 16)
    comment2num = lambda _: int(datas[TelDict[_]], 16)
    # 起始角度
    startangle = comment2num('Start Angle') / 10000
    # 角度分辨率
    anglestep = 2.0 / round(20000.0 / comment2num('Steps'))
    # 测量得数据总量
    datanum = comment2num('Amount of Data')
    if datanum == 0:
        return []
    points = np.zeros((datanum, 3), dtype=np.float32)
    point = np.zeros(3, dtype=np.float32)
    for i in range(datanum):
        try:
            #        radius     ,      unit:mm , double or not         angle factor    ,          degree to arc
            point[0] = index2num(TelDict['Data'] + i) / 1000 * factors * math.cos(
                (startangle + i * anglestep) / 180 * math.pi)
            point[1] = index2num(TelDict['Data'] + i) / 1000 * factors * math.sin(
                (startangle + i * anglestep) / 180 * math.pi)
            point[2] = 0
            points[i] = point
        except Exception as e:
            print("exception:", e)
            print('i = %d ' % i + 'datanum: %d ' % datanum)
            # print('the raw data is : ' + raw_data)
            break
    return points


# sSN
# def Debug_rounddata_process(data_long, now_in_period, period):
#     # left lay down
#     # data_long = data_long.decode()
#     data_long = data_long[1:-1]
#     data = data_long.split(' ')
#     if not data[0] == "sSN":
#         print('error data:' + data_long)
#         return []
#     # if data[-1].endswith('\x03'):
#     #     data[-1] = data[-1][:-1]
#     if data[21] == '40000000':
#         factors = 2
#     elif data[21] == '3F800000':
#         factors = 1
#     else:
#         print('error data')
#         return []
#     print('start_time:', int(data[8], 16))
#     startangle = int(data[23], 16) / 10000
#     anglestep = 2.0 / round(20000.0 / int(data[24], 16))
#     datanum = int(data[25], 16)
#     points = []
#
#     phi = now_in_period / period * 2 * math.pi
#     for i in range(datanum):
#         try:
#             point = []
#             radius = int(data[26 + i], 16) / 1000 * factors
#             theta = (startangle + i * anglestep) / 180 * math.pi
#             point.append(radius * math.sin(theta) * math.cos(phi))  # X
#             point.append(radius * math.sin(theta) * math.sin(phi))  # Y
#             point.append(radius * math.cos(theta))  # Z
#             points.append(point)
#         except Exception as e:
#             print("exception:", e)
#             print("at time:%d, data num: %d, in [%d]" % (now_in_period, datanum, i))
#             # print('the raw data is : ' + raw_data)
#             print('i = %d ' % i + 'datanum: %d ' % datanum)
#             break
#     return points

# sRA
def Debug_rounddata_process(dataB, now_in_period, period):
    # left lay down
    dataB = dataB[1:-1]
    dataStr = dataB.decode('ascii')
    datas = dataStr.split(' ')
    if not datas[0] == "sRA":
        print('error data:' + dataStr)
        return []

    ContentIndex = datas.index('DIST1')
    for index, comment in zip(range(len(SubTgList)), SubTgList):
        TelDict[comment] = ContentIndex + index
    # 回波系数，乘数
    factorHex = datas[TelDict['Scale Factor']]
    if factorHex == '40000000':
        factors = 2
    elif factorHex == '3F800000':
        factors = 1
    else:
        print('error data:' + dataStr)
        return []

    index2num = lambda _: int(datas[_], 16)
    comment2num = lambda _: int(datas[TelDict[_]], 16)

    # 起始角度
    startangle = comment2num('Start Angle') / 10000
    # 角度分辨率
    anglestep = 2.0 / round(20000.0 / comment2num('Steps'))
    # 测量得数据总量
    datanum = comment2num('Amount of Data')
    if datanum == 0:
        return []
    points = np.zeros((datanum, 3), dtype=np.float32)
    point = np.zeros(3, dtype=np.float32)
    phi = now_in_period / period * 2 * math.pi
    for i in range(datanum):
        try:
            radius = index2num(TelDict['Data'] + i) / 1000 * factors
            theta = (startangle + i * anglestep) / 180 * math.pi
            point[0] = radius * math.sin(theta) * math.cos(phi)  # X
            point[1] = radius * math.sin(theta) * math.sin(phi)  # Y
            point[2] = radius * math.cos(theta)  # Z
            points[i] = point
        except Exception as e:
            print("exception:", e)
            print("at time:%d, data num: %d, in [%d]" % (now_in_period, datanum, i))
            # print('the raw data is : ' + raw_data)
            print('i = %d ' % i + 'datanum: %d ' % datanum)
            break
    return points
