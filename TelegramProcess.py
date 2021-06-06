import math


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
    anglestep = 2.0 / round(20000.0 / int(data[24], 16))
    # 测量得数据总量
    datanum = int(data[25], 16)
    if datanum == 0:
        return []
    points = []

    for i in range(datanum):
        try:
            point = []
            #        radius     ,      unit:mm , double or not         angle factor    ,          degree to arc
            point.append(
                int(data[26 + i], 16) / 1000 * factors * math.cos((startangle + i * anglestep) / 180 * math.pi))
            point.append(
                int(data[26 + i], 16) / 1000 * factors * math.sin((startangle + i * anglestep) / 180 * math.pi))
            point.append(0)
            points.append(point)
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
def Debug_rounddata_process(data_long, now_in_period, period):
    # left lay down
    # data_long = data_long.decode()
    data_long = data_long[1:-1]
    data = data_long.split(' ')
    if not data[0] == "sRA":
        print('error data:'+data_long)
        return []
    # if data[-1].endswith('\x03'):
    #     data[-1] = data[-1][:-1]
    if data[21] == '40000000':
        factors = 2
    elif data[21] == '3F800000':
        factors = 1
    else:
        print('error data')
        return []
    print('start_time:',int(data[8],16))
    startangle = int(data[23], 16) / 10000
    anglestep = 2.0 / round(20000.0 / int(data[24], 16))
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
            print('i = %d ' % i + 'datanum: %d ' % datanum)
            break
    return points
