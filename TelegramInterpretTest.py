import numpy as np
import math

# a example of received data
dataB = b'\x02sRA LMDscandata 0 1 119883A 0 0 2796 2801 F87F5C00 F87FA401 0 0 3F 0 0 1388 168 0 1 DIST1 40000000 00000000 0 1388 F1 363 364 35B 35A 35A 342 33F 33E 341 344 341 353 35A 35F 35D 37A 38E 38E 39A 3A4 3A6 3AE 3B8 3BF 3C3 3C2 3C5 3CE 3D6 3DA 3E0 3E3 3E0 3E5 3E9 3E6 3EB 3EF 3F4 410 4E5 4FB 501 505 508 50B 511 518 51E 4E0 4D5 4E2 51B 4E4 4D0 4F9 4DE 4BC 4B2 4B4 49D 48E 484 481 484 487 491 495 49E 4A9 4AD 4B1 4BB 4C2 4CD 4D3 4DB 4E9 4ED 4F7 4FD 508 50E 51D 525 531 53C 544 551 55C 567 570 57D 58D 596 5A5 5B1 5C0 5D0 5E0 5EE 5FD 60E 622 62F 63F 64D 664 676 689 6A0 6B6 6C9 6DD 6F8 70C 725 73B 756 76E 789 7A8 7C4 7E0 804 823 844 865 88D 8AF 8D2 8FE 926 956 982 9B0 9E3 A17 A50 A84 ABD B02 B41 B85 BD3 C1D C6F CC2 D1A D76 DE3 E5D EDC F5E FF2 1095 1146 11FD 12D3 13C8 14BB 15CB 16EC 185A 1941 194F 1948 1945 194C 1958 1957 1962 1966 0 0 7B96 7B98 7BA9 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0\x03'
dataB = dataB[1:-1]
dataStr = dataB.decode('ascii')
# dataStr = 'sRA LMDscandata 0 1 119883A 0 0 2796 2801 F87F5C00 F87FA401 0 0 3F 0 0 1388 168 0 1 DIST1 40000000 00000000 0 1388 F1 363 364 35B 35A 35A 342 33F 33E 341 344 341 353 35A 35F 35D 37A 38E 38E 39A 3A4 3A6 3AE 3B8 3BF 3C3 3C2 3C5 3CE 3D6 3DA 3E0 3E3 3E0 3E5 3E9 3E6 3EB 3EF 3F4 410 4E5 4FB 501 505 508 50B 511 518 51E 4E0 4D5 4E2 51B 4E4 4D0 4F9 4DE 4BC 4B2 4B4 49D 48E 484 481 484 487 491 495 49E 4A9 4AD 4B1 4BB 4C2 4CD 4D3 4DB 4E9 4ED 4F7 4FD 508 50E 51D 525 531 53C 544 551 55C 567 570 57D 58D 596 5A5 5B1 5C0 5D0 5E0 5EE 5FD 60E 622 62F 63F 64D 664 676 689 6A0 6B6 6C9 6DD 6F8 70C 725 73B 756 76E 789 7A8 7C4 7E0 804 823 844 865 88D 8AF 8D2 8FE 926 956 982 9B0 9E3 A17 A50 A84 ABD B02 B41 B85 BD3 C1D C6F CC2 D1A D76 DE3 E5D EDC F5E FF2 1095 1146 11FD 12D3 13C8 14BB 15CB 16EC 185A 1941 194F 1948 1945 194C 1958 1957 1962 1966 0 0 7B96 7B98 7BA9 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0'
datas = dataStr.split(' ')
# compared with the telegram protocol , explain data in following comment
TelegramList = ['Command Type', 'Command', 'Version Number', 'Device Number', 'Serial Number',
                'Device Status 1 00=OK', 'Device Status 2 00=OK', 'Telegram Counter',
                'Scan Counter', 'Time Since Start Up', 'Time of Transmission', 'Status of Digital Input 1',
                'Status of Digital Input2', 'Status of Digital Output 1', 'Status of Digital Output 2',
                'Reserved', 'Scan Frequency', 'Mesurement Frequency', 'Encoder Position', 'Encoder Speed',
                'Content', 'Scale Factor', 'Scale Factor Offset', 'Start Angle', 'Steps', 'Amount of Data']
#        add Data
TelegramList = TelegramList + ['Data'] * (int(datas[TelegramList.index('Amount of Data')], 16))
#        add Space until the end
TelegramList = TelegramList + ['???'] * (len(datas) - len(TelegramList))
bindDatas = [[index, comment, data] for index, comment, data in zip(range(len(datas)), TelegramList, datas)]
# show the corresponded explaination in example data
print(bindDatas)

# because random errors often occur , better to check the data smartly
# find the Content Data as beginning
TelDict = {}
ContentIndex = datas.index('DIST1')
# TelDict['Content']=CommentIndex  # Not necessarily
SubTgList = ['Content', 'Scale Factor', 'Scale Factor Offset', 'Start Angle', 'Steps', 'Amount of Data', 'Data']
for index, comment in zip(range(len(SubTgList)), SubTgList):
    TelDict[comment] = ContentIndex + index
print(TelDict)

factorHex = datas[TelDict['Scale Factor']]
factors = 0
if factorHex == '40000000':
    factors = 2
elif factorHex == '3F800000':
    factors = 1
else:
    exec('error')


def hex2num(data):
    return int(data, 16)


def comment2num(comment):
    return int(datas[TelDict[comment]], 16)


# 起始角度
startangle = comment2num('Start Angle') / 10000
# 角度分辨率
anglestep = 2.0 / round(20000.0 / comment2num('Steps'))
# 测量得数据总量
datanum = comment2num('Amount of Data')

points = np.zeros((datanum, 3), dtype=np.float32)
point = np.zeros(3, dtype=np.float32)
for i in range(datanum):
    try:
        #        radius     ,      unit:mm , double or not         angle factor    ,          degree to arc
        point[0] = hex2num(datas[26 + i]) / 1000 * factors * math.cos((startangle + i * anglestep) / 180 * math.pi)
        point[1] = int(datas[26 + i], 16) / 1000 * factors * math.sin((startangle + i * anglestep) / 180 * math.pi)
        point[2] = 0
        points[i] = point
    except Exception as e:
        print("exception:", e)
        print('i = %d ' % i + 'datanum: %d ' % datanum)
        # print('the raw data is : ' + raw_data)
        break
