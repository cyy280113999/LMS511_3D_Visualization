import time
import threading
import socket
import numpy as np


# 登录
# "\x02sMN SetAccessMode 03 F4724744\x03"
# "\x02sAN SetAccessMode 1\x03"
# 设置角度分辨率
# "\x02sMN mLMPsetscancfg 9C4 1 9C4 FFFF3CB0 1C3A90\x03"
# "\x02sAN mLMPsetscancfg 0 9C4 1 9C4 FFFF3CB0 1C3A90\x03"
# 设置角度范围
# "\x02sWN LMPoutputRange 1 +5000 +450000 +1350000\x03"
# "\x02sWA LMPoutputRange\x03"
# 存储参数
# "\x02sMN mEEwriteall\x03"
# "\x02sAN mEEwriteall 1\x03"
# 退出登录
# "\x02sMN Run\x03"
# "\x02sAN Run 1\x03"
# 扫描一次
# "\x02sRN LMDscandata\x03"
# --回复？


# sock state
class AbstractState:
    # 抽象状态
    def __init__(self, stateStrList, link, state=''):
        # if stateStrList is None or link is None:
        #     return
        self.stateStrList = stateStrList
        self.stateStrDict = dict()
        for i in range(len(self.stateStrList)):
            self.stateStrDict[self.stateStrList[i]] = i
        self.link = link

        if state in self.stateStrList:
            self.stateValue = self.stateStrDict[state]
        else:
            self.stateValue = 0
        self.stateStr = self.stateStrList[self.stateValue]
        return

    def getState(self):
        return self.stateStr

    def toState(self, state):
        if state not in self.stateStrList:
            print('Error : %s is not a valid state to change to! You should pick state from : %s'
                  % (state, self.stateStrList))
            return
        # 查看状态转移矩阵是否允许转移
        if self.link[self.stateValue][self.stateStrDict[state]] == 1:
            self.stateStr = state
            self.stateValue = self.stateStrDict[self.stateStr]
        else:
            print('Warning : Can not change state from %s to %s !'
                  % (self.stateStr, state))


class State(AbstractState):

    def __init__(self):
        stateStrList = ['unconnect', 'running', 'setting', 'reading', 'round reading']
        link = [[1, 1, 0, 0, 0],
                [1, 1, 1, 1, 1],
                [1, 1, 1, 0, 0],
                [1, 1, 0, 1, 0],
                [1, 1, 0, 0, 1]]

        super().__init__(stateStrList, link, 'unconnect')

    def isUnconnect(self):
        return self.stateValue == self.stateStrDict['unconnect']

    # deleted state : connected. Same function as running
    # def toConnected(self):
    #     self.toState('connected')
    #
    # def isConnected(self):
    #     return self.stateValue == self.stateStrDict['connected']

    def toRunning(self):
        self.toState('running')

    def isRunning(self):
        return self.stateValue == self.stateStrDict['running']

    def toSetting(self):
        self.toState('setting')

    def isSetting(self):
        return self.stateValue == self.stateStrDict['setting']

    def toReading(self):
        self.toState('reading')

    def isReading(self):
        return self.stateValue == self.stateStrDict['reading']

    def toRoundReading(self):
        self.toState('round reading')

    def isRoundReading(self):
        return self.stateValue == self.stateStrDict['round reading']

    def toUnconnect(self):
        self.toState('unconnect')


bufsiz = 8192


class MySock:
    #               connected_true
    #              |             \
    #        run_true             run_false
    #       |       \                 \
    # reading_true  reading_false     set_paraments
    state = State()

    read_off_flag = False
    reading_200_times_debug = False
    round_read_debug = False
    # no use
    connected = False
    run = False
    reading = False

    def __init__(self, master):
        self.master = master
        # use explicit ip
        self.ip = "169.254.104.114"
        self.port = 2111
        self.addr = (self.ip, self.port)

    def connect(self, addr: tuple = None):
        if self.state.isUnconnect():  # #####
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setblocking(True)
            # self.sock.settimeout(10)
            try:
                if addr is None:
                    self.sock.connect(self.addr)
                else:
                    self.ip = addr[0]
                    self.port = addr[1]
                    self.addr = addr
                    self.sock.connect(addr)
            except socket.error as e:
                print(e)
                self.master.warning_information('Connect failed! To:' + self.ip + ':' + str(self.port))
            else:
                self.state.toRunning()  # #####
                self.master.showInMessageBar("Connected to" + self.ip + ':' + str(self.port))
                self.master.add_information("Connected to %s : %s ." % (self.ip, str(self.port)))
                # self.master.connect_btn.setEnabled(False)
        else:
            self.master.add_information('already connected.')
        return

    def readonce(self):
        if self.state.isRunning():
            self.state.toReading()
            self.master.read_once_btn.setEnabled(False)
            time1 = time.time()
            send_data = b'\x02sRN LMDscandata\x03'
            self.sock.send(send_data)
            self.master.add_information('sended:' + send_data.decode())
            recv_data = self.sock.recv(bufsiz)
            time2 = time.time()
            data = recv_data.decode()
            self.master.add_information('received:' + data)
            self.master.add_information("communication time %f" % (time2 - time1))
            time3 = time.time()
            self.master.process_once_data(data)
            time4 = time.time()
            self.master.add_information("processing time %f" % (time4 - time3))
            self.master.add_information("totally cost %f" % (time4 - time1))
            self.master.read_once_btn.setEnabled(True)
            self.state.toRunning()
        elif self.state.isUnconnect():
            self.master.warning_information('should first connect!')
        elif self.state.isSetting():
            self.master.warning_information('cannot read during setting paraments!')
        elif self.state.isReading() | self.state.isRoundReading():
            self.master.warning_information('reading conflict!')
        else:
            self.master.warning_information('Unknown Error!')
        return

    def readalways(self):
        if self.state.isRunning():
            self.master.read_always_btn.Text_On()
            self.reading_ptr = threading.Thread(target=readalways_fun, args=(self,))
            self.reading_ptr.start()
        elif self.state.isReading():
            self.read_off_flag = True

        elif self.state.isUnconnect():
            self.master.warning_information('should first connect!')
        elif self.state.isSetting():
            self.master.warning_information('cannot read during setting paraments!')
        elif self.state.isRoundReading():
            self.master.warning_information('reading conflict!')
        else:
            self.master.warning_information('Unknown Error!')
        return

    # no use
    def _read_200_times(self):
        if self.connected:
            if self.run:
                if not self.reading:
                    if not self.reading_200_times_debug:
                        self.master.RoundModeBtn.setText("Scanning")
                        self.master.RoundModeBtn.setEnabled(False)
                        self.reading_200_times_debug = True
                        self.reading = True
                        reading_200_times_ptr = threading.Thread(target=reading_200_times_fun, args=(self,))
                        reading_200_times_ptr.start()

                else:
                    self.master.Debug_Add_Info('error : is reading!')

            else:
                self.master.Debug_Add_Info('cannot read during setting paraments')
        else:
            self.master.Debug_Add_Info('first connect!')

    def round_read(self, period, gap):
        if self.state.isRunning():
            self.master.progressBar.setVisible(True)
            self.master.progressBar.setValue(0)
            self.master.RoundModeBtn.setText("Press to stop")
            round_read_ptr = threading.Thread(target=round_read_fun, args=(self, period, gap))
            round_read_ptr.start()
        elif self.state.isRoundReading():
            self.read_off_flag = True

        elif self.state.isUnconnect():
            self.master.warning_information('should first connect!')
        elif self.state.isSetting():
            self.master.warning_information('cannot read during setting paraments!')
        elif self.state.isReading():
            self.master.warning_information('reading conflict!')
        else:
            self.master.warning_information('Unknown Error!')
        return

    def login(self):
        if self.state.isRunning():
            logindata = b"\x02sMN SetAccessMode 03 F4724744\x03"
            self.sock.send(logindata)
            login_return = self.sock.recv(bufsiz)
            if login_return == b"\x02sAN SetAccessMode 1\x03":
                self.state.toSetting()
                # self.master.login_btn   off
                # self.master.logout_btn   on
                self.master.add_information('log in success')
            else:
                self.master.warning_information('login error')
                self.master.add_information(login_return.decode())
        elif self.state.isSetting():
            self.master.warning_information('already log in')
        elif self.state.isUnconnect():
            self.master.warning_information('should first connect!')
        elif self.state.isReading() | self.state.isRoundReading():
            self.master.warning_information('should stop reading!')
        else:
            self.master.warning_information('Unknown Error!')

    def logout(self):
        if self.state.isSetting():
            logoutdata = b"\x02sMN Run\x03"
            self.sock.send(logoutdata)
            logout_return = self.sock.recv(bufsiz)
            if logout_return == b"\x02sAN Run 1\x03":
                self.state.toRunning()
                # self.master.login_btn  ON
                # self.master.logout_btn  Off
                self.master.add_information('log out success')
            else:
                self.master.warning_information('logout failed' + logout_return.decode())
                self.master.add_information(logout_return.decode())
        elif self.state.isRunning():
            self.master.warning_information('repeatedly operation')
        elif self.state.isUnconnect():
            self.master.warning_information('should first connect!')
        elif self.state.isReading() | self.state.isRoundReading():
            self.master.warning_information('should stop reading and log in!')
        else:
            self.master.warning_information('Unknown Error!')

    def savepara(self):
        if self.state.isSetting():
            try:
                savedata = b"\x02sMN mEEwriteall\x03"
                self.sock.send(savedata)
                save_return = self.sock.recv(bufsiz)
                if save_return == b"\x02sAN mEEwriteall 1\x03":
                    self.master.add_information('save paraments success')
                else:
                    self.master.warning_information('save failed')
                    self.master.add_information(save_return.decode())
            except Exception as e:
                print(e)
        elif self.state.isRunning():
            self.master.warning_information('please log in')
        elif self.state.isUnconnect():
            self.master.warning_information('should first connect!')
        elif self.state.isReading() | self.state.isRoundReading():
            self.master.warning_information('should stop reading and log in!')
        else:
            self.master.warning_information('Unknown Error!')

    def change_freq(self, freq, resl):
        # print(freq, resl)
        if self.state.isSetting():
            try:
                angle_data = "\x02sMN mLMPsetscancfg +{} 1 +{} +00000 +1800000\x03". \
                    format(freq, resl)
                angle_data = angle_data.encode('ascii')
                self.sock.send(angle_data)
                angle_return = self.sock.recv(bufsiz).decode()
                angle_return2 = angle_return.split(' ')
                if ' '.join(angle_return2[0:2]) == "\x02sAN mLMPsetscancfg" and angle_return2[2] == '0':
                    self.master.add_information('frequency change success')
                else:
                    self.master.warning_information('frequency change failed')
                    self.master.add_information(angle_return)
            except Exception as e:
                print(e)
        elif self.state.isRunning():
            self.master.warning_information('please log in')
        elif self.state.isUnconnect():
            self.master.warning_information('should first connect!')
        elif self.state.isReading() | self.state.isRoundReading():
            self.master.warning_information('should stop reading and log in!')
        else:
            self.master.warning_information('Unknown Error!')

    def change_angle(self, angle_min=0, angle_max=180):
        if self.state.isSetting():
            try:
                if angle_min >= angle_max or angle_max < 0:
                    self.master.warning_information('unvalid value')
                    return
                angle_data = "\x02sWN LMPoutputRange 1 +5000 {}{}0000 +{}0000\x03".format(
                    '+' if angle_min >= 0 else '', int(angle_min), int(angle_max))
                angle_data = angle_data.encode('ascii')
                self.sock.send(angle_data)
                angle_return = self.sock.recv(bufsiz)
                if angle_return == b"\x02sWA LMPoutputRange\x03":
                    self.master.add_information('angle change success')
                else:
                    self.master.warning_information('angle change failed')
            except Exception as e:
                print(e)
        elif self.state.isRunning():
            self.master.warning_information('please log in')
        elif self.state.isUnconnect():
            self.master.warning_information('should first connect!')
        elif self.state.isReading() | self.state.isRoundReading():
            self.master.warning_information('should stop reading and log in!')
        else:
            self.master.warning_information('Unknown Error!')

    def changeip(self, ip):
        if self.state.isSetting():
            try:
                ip_hexstr = iptohex(ip)
                ip_data = "\x02sWN EIIpAddr {}\x03".format(ip_hexstr)
                ip_data = ip_data.encode('ascii')
                self.sock.send(ip_data)
                ip_return = self.sock.recv(bufsiz)
                if ip_return == b"\x02sWA EIIpAddr\x03":
                    self.master.add_information('ip change success')
                else:
                    self.master.warning_information('ip change failed')
            except Exception as e:
                print(e)
        elif self.state.isRunning():
            self.master.warning_information('please log in')
        elif self.state.isUnconnect():
            self.master.warning_information('should first connect!')
        elif self.state.isReading() | self.state.isRoundReading():
            self.master.warning_information('should stop reading and log in!')
        else:
            self.master.warning_information('Unknown Error!')

    def reboot(self):
        if self.state.isRunning() or self.state.isSetting():
            try:
                data = "\x02sMN mSCreboot\x03"
                data = data.encode('ascii')
                self.sock.send(data)
                return_ = self.sock.recv(bufsiz)
                if return_ == b"\x02sAN mSCreboot\x03":
                    self.master.add_information('waiting for reboot')
                    self.sock.shutdown(2)
                    self.state.toUnconnect()
                    self.master.showInMessageBar("Unconnect")
                    # self.master.connect_btn.setEnabled(True)
                else:
                    self.master.warning_information('reboot failed')
            except Exception as e:
                print(e)
        elif self.state.isUnconnect():
            self.master.warning_information('should first connect!')
        elif self.state.isReading() | self.state.isRoundReading():
            self.master.warning_information('should stop reading!')
        else:
            self.master.warning_information('Unknown Error!')


# thread functions
def readalways_fun(mysock: MySock):
    mysock.state.toReading()
    send_data = b'\x02sRN LMDscandata\x03'
    while not mysock.read_off_flag:
        try:
            time1 = time.time()
            mysock.sock.send(send_data)
            mysock.master.add_information('sended:' + send_data.decode())
            recv_data = mysock.sock.recv(bufsiz)
            data = recv_data.decode()
            mysock.master.add_information('received:' + data)
            time2 = time.time()
            mysock.master.add_information("communication time %f" % (time2 - time1))
            time3 = time.time()
            mysock.master.process_once_data(data)
            time4 = time.time()
            mysock.master.add_information("processing time %f" % (time4 - time3))
        except socket.error as e:
            print(e)
        time.sleep(0.05)
    mysock.read_off_flag = False
    mysock.state.toRunning()
    mysock.master.read_always_btn.Text_Off()


# def round_read_fun(mysock: MySock, period, gap):
#     mysock.state.toRoundReading()
#     mysock.master.pointCloud.clearPoints()
#     send_data = b'\x02sEN LMDscandata 1\x03'
#     mysock.sock.send(send_data)
#     recv_data = mysock.sock.recv(bufsiz)
#     if recv_data != b'\x02sEA LMDscandata 1\x03':
#         print('start failed')
#         return
#     total_start_time = time.time()
#     print("start at:"+time.asctime()+'. s:', time.time())
#     try:
#         while not mysock.read_off_flag:
#             now_start_time = time.time()
#             if now_start_time - total_start_time > period:
#                 break
#             recv_data = mysock.sock.recv(bufsiz)
#             data = recv_data.decode()
#             mysock.master.process_round_data(data, now_start_time - total_start_time, period)
#             mysock.master.progressBar.setValue(round((now_start_time - total_start_time) * 100 / period))
#             # time.sleep(gap)
#         send_data = b'\x02sEN LMDscandata 0\x03'
#         mysock.sock.send(send_data)
#         recv_data = mysock.sock.recv(bufsiz)
#         # receive twice
#         if recv_data != b'\x02sEA LMDscandata 0\x03':
#             print('stop failed 1', recv_data)
#             time.sleep(1)
#             recv_data = mysock.sock.recv(bufsiz)
#             if recv_data != b'\x02sEA LMDscandata 0\x03':
#                 print('stop failed 2', recv_data)
#                 return
#         mysock.master.RoundModeBtn.setText("Round Scan")
#         mysock.read_off_flag = False
#         # mysock.master.progressBar.setVisible(False)
#         mysock.state.toRunning()
#     except Exception as e:
#         print(e)
#     # print("stop at:" + time.asctime()+'. s:', time.time())

# back up
def round_read_fun(mysock: MySock, period, gap):
    mysock.state.toRoundReading()
    mysock.master.pointCloud.clearPoints()
    send_data = b'\x02sRN LMDscandata\x03'
    total_start_time = time.time()
    print("start at:"+time.asctime()+'. s:', time.time())
    try:
        while not mysock.read_off_flag:
            now_start_time = time.time()
            if now_start_time - total_start_time > period:
                break
            try:
                mysock.sock.send(send_data)
                recv_data = mysock.sock.recv(bufsiz)
                data = recv_data.decode()
                mysock.master.process_round_data(data, now_start_time - total_start_time, period)
                mysock.master.progressBar.setValue(round((now_start_time - total_start_time) * 100 / period))
            except socket.error as e:
                print(e)
            time.sleep(gap)
    except Exception as e:
        print(e)
    try:
        mysock.master.RoundModeBtn.setText("Round Scan")
        mysock.read_off_flag = False
        # mysock.master.progressBar.setVisible(False)
        mysock.state.toRunning()
    except Exception as e:
        print(e)
    print("stop at:" + time.asctime()+'. s:', time.time())

# no use
def _reading_200_times_fun(_msock):
    send_data = b'\x02sRN LMDscandata\x03'
    for temp_time in range(200):
        start_time = time.time()
        _msock.s.send(send_data)
        recv_data = _msock.s.recv(bufsiz)
        time3 = time.time()
        data = recv_data.decode()
        _msock.master.process_round_data(data, temp_time)
        time4 = time.time()
        _msock.master.Debug_Add_Info("processing time %f" % (time4 - time3))
        stop_time = time.time()
        left_time = 0.1 - (stop_time - start_time)
        if left_time >= 0:
            _msock.master.Debug_Add_Info("left time %f" % left_time)
            time.sleep(left_time)
    _msock.master.RoundModeBtn.setText("Round Scan")
    _msock.master.RoundModeBtn.setEnabled(True)
    _msock.reading_200_times_debug = False
    _msock.reading = False


# no use , for equal_interval scan, instead of scan in real_time
def _old_round_read_fun(mysock: MySock, period, gap):
    total_times = int(period / gap)
    send_data = b'\x02sRN LMDscandata\x03'

    begin_time = time.time()
    total_lost_time = 0
    for temp_time in range(total_times):
        if temp_time > 0:
            while time.time() < mysock.last_start_time + gap:
                time.sleep(0.0001)
            lost_time = time.time() - (mysock.last_start_time + gap)
            total_lost_time = total_lost_time + lost_time
            if lost_time > 0.005:
                print("time lost:%f" % lost_time)
        start_time = time.time()
        mysock.sock.send(send_data)
        recv_data = mysock.sock.recv(bufsiz)

        data = recv_data.decode()
        mysock.master.process_round_data_later(data, temp_time, total_times)
        mysock.last_start_time = start_time
        # stop_time = time.time()
        # left_time = gap-(stop_time-start_time)
        mysock.master.Debug_Add_Info("start time %f" % start_time)
        # _msock.master.Debug_Add_Info("left time %f" % (left_time))

    end_time = time.time()
    mysock.master.Debug_Add_Info("begin at:%f, end at:%f, cost:%f" % (begin_time, end_time, end_time - begin_time))
    print("total_lost_time:%f" % total_lost_time)


# utility
def iptohex(ip: str):
    iplist = ip.split('.')
    return ' '.join([strtohex2(str_) for str_ in iplist])


def strtohex1(str_):
    num = int(str_)
    return (hex(num // 16)[2:] + hex(num % 16)[2:]).upper()


def strtohex2(str_):
    num = int(str_)
    return hex(num)[2:].upper()