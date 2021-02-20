import time
import threading
import socket
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
bufsiz=8192


class MySock:
    #               connected_true
    #              |             \
    #        run_true             run_false
    #       |       \                 \
    # reading_true  reading_false     set_paraments
    connected = False
    run = False
    reading = False
    read_off_flag = False

    reading_200_times_debug = False
    round_read_debug = False

    def __init__(self,master):
        self.master=master
        self.s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.ip = "169.254.104.114"
        self.port = 2111
        self.addr = (self.ip,self.port)

    def connect(self):
        if not self.connected:
            try:
                self.s.connect(self.addr)

            except Exception as e:
                self.master.Debug_Add_Info('connect failed')
            else:
                self.connected = True
                self.run = True
                self.master.statusBar().showMessage("connected to" + self.ip + ':' + str(self.port))
                self.master.Debug_Add_Info('connected')
                self.master.connect_btn.setEnabled(False)
        else:self.master.Debug_Add_Info('already!')

    def readonce(self):
        if self.connected:
            if self.run:
                if not self.reading:
                    self.master.read_once_btn.setEnabled(False)
                    time1=time.time()
                    send_data = b'\x02sRN LMDscandata\x03'
                    self.s.send(send_data)
                    self.master.Debug_Add_Info('sended:' + send_data.decode())
                    recv_data = self.s.recv(bufsiz)
                    time2=time.time()
                    data = recv_data.decode()
                    self.master.Debug_Add_Info('received:'+data)
                    self.master.Debug_Add_Info("communication time %f"%(time2-time1))
                    time3 = time.time()
                    self.master.process_once_data(data)
                    time4 = time.time()
                    self.master.Debug_Add_Info("processing time %f" % (time4 - time3))
                    self.master.read_once_btn.setEnabled(True)
                else:
                    self.master.Debug_Add_Info("running 'read always'!")
            else:
                self.master.Debug_Add_Info('cannot read during setting paraments')
        else:
            self.master.Debug_Add_Info('should first connect!')

    def readalways(self):
        if self.connected:
            if self.run:
                if not self.reading:
                    self.master.read_always_btn.Text_On()
                    self.reading_ptr = threading.Thread(target=self.readalways_fun, args=(self,))
                    self.reading_ptr.start()
                else:
                    self.read_off_flag = True
                    self.master.read_always_btn.Text_Off()
            else:
                self.master.Debug_Add_Info('cannot read during setting paraments')
        else:
            self.master.Debug_Add_Info('first connect!')

    def readalways_fun(self,_msock):
        _msock.reading = True

        while not _msock.read_off_flag:
            if _msock.connected:
                if _msock.run:
                    send_data = b'\x02sRN LMDscandata\x03'
                    _msock.s.send(send_data)
                    _msock.master.Debug_Add_Info('sended:' + send_data.decode())
                    recv_data = _msock.s.recv(bufsiz)
                    data = recv_data.decode()
                    _msock.master.Debug_Add_Info('received:' + data)
                    _msock.master.process_once_data(data)
                else:
                    _msock.master.Debug_Add_Info('cannot read during setting paraments')
            else:
                _msock.master.Debug_Add_Info('should first connect!')
            time.sleep(0.05)
        _msock.read_off_flag=False
        _msock.reading = False

    def read_200_times(self):
        if self.connected:
            if self.run:
                if not self.reading:
                    if not self.reading_200_times_debug:
                        self.master.RoundModeBtn.setText("Scanning")
                        self.master.RoundModeBtn.setEnabled(False)
                        self.reading_200_times_debug = True
                        self.reading = True
                        reading_200_times_ptr = threading.Thread(target=self.reading_200_times_fun, args=(self,))
                        reading_200_times_ptr.start()

                else:
                    self.master.Debug_Add_Info('error : is reading!')

            else:
                self.master.Debug_Add_Info('cannot read during setting paraments')
        else:
            self.master.Debug_Add_Info('first connect!')

    def reading_200_times_fun(self,_msock):

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
            left_time = 0.1-(stop_time-start_time)
            if left_time >= 0:
                _msock.master.Debug_Add_Info("left time %f" % (left_time))
                time.sleep(left_time)
        _msock.master.RoundModeBtn.setText("Round Scan")
        _msock.master.RoundModeBtn.setEnabled(True)
        _msock.reading_200_times_debug = False
        _msock.reading = False

    def round_read(self, period, gap):
        if self.connected:
            if self.run:
                if not self.reading:
                    if not self.round_read_debug:
                        self.master.RoundModeBtn.setText("Scanning")
                        self.master.RoundModeBtn.setEnabled(False)
                        self.round_read_debug = True
                        self.reading = True
                        round_read_ptr = threading.Thread(target=self.round_read_fun, args=(self, period, gap))
                        round_read_ptr.start()

                else:
                    self.master.Debug_Add_Info('error : is reading!')

            else:
                self.master.Debug_Add_Info('cannot read during setting paraments')
        else:
            self.master.Debug_Add_Info('first connect!')

    def round_read_fun(self, _msock, period, gap):
        _msock.master.pointCloud.clearPoints()

        send_data = b'\x02sRN LMDscandata\x03'
        total_start_time=time.time()
        while True:
            now_start_time=time.time()
            if now_start_time-total_start_time > period:
                break
            _msock.s.send(send_data)
            recv_data = _msock.s.recv(bufsiz)
            data = recv_data.decode()
            _msock.master.process_round_data2(data, now_start_time-total_start_time, period)

            time.sleep(gap)


        # total_times = int(period/gap)
        # send_data = b'\x02sRN LMDscandata\x03'
        #
        #
        # begin_time = time.time()
        # total_lost_time = 0
        # for temp_time in range(total_times):
        #     if temp_time > 0:
        #         while time.time() < _msock.last_start_time + gap:
        #             time.sleep(0.0001)
        #         lost_time = time.time() - (_msock.last_start_time + gap)
        #         total_lost_time=total_lost_time+lost_time
        #         if lost_time > 0.005:
        #             print("time lost:%f" % (lost_time))
        #     start_time = time.time()
        #     _msock.s.send(send_data)
        #     recv_data = _msock.s.recv(bufsiz)
        #
        #
        #
        #     data = recv_data.decode()
        #     _msock.master.process_round_data_later(data, temp_time, total_times)
        #     _msock.last_start_time = start_time
        #     #stop_time = time.time()
        #     #left_time = gap-(stop_time-start_time)
        #     _msock.master.Debug_Add_Info("start time %f" % (start_time))
        #     #_msock.master.Debug_Add_Info("left time %f" % (left_time))
        #
        #
        #
        # end_time = time.time()
        # _msock.master.Debug_Add_Info("begin at:%f, end at:%f, cost:%f" % (begin_time,end_time,end_time-begin_time))
        # print("total_lost_time:%f"%(total_lost_time))

        _msock.master.RoundModeBtn.setText("Round Scan")
        _msock.master.RoundModeBtn.setEnabled(True)
        _msock.round_read_debug = False
        _msock.reading = False

    def angle_interval(self,angle_min = 0, angle_max = 180):
        if self.connected:
            if self.run:
                logindata=b"\x02sMN SetAccessMode 03 F4724744\x03"
                self.s.send(logindata)
                login_return = self.s.recv(bufsiz)
                if login_return == b"\x02sAN SetAccessMode 1\x03":
                    self.run = False
                    angle_data = "\x02sWN LMPoutputRange 1 +5000 +{}0000 +{}0000\x03".format(angle_min,angle_max)
                    angle_data = angle_data.encode('ascii')
                    self.s.send(angle_data)
                    angle_return = self.s.recv(bufsiz)
                    if angle_return == b"\x02sWA LMPoutputRange\x03":
                        self.master.Debug_Add_Info('angle interval change success')
                    else:
                        self.master.Debug_Add_Info('angle interval change failed')
                    logoutdata = b"\x02sMN Run\x03"
                    self.s.send(logoutdata)
                    logout_return = self.s.recv(bufsiz)
                    if logout_return == b"\x02sAN Run 1\x03":
                        self.run = True
                    else:
                        self.master.Debug_Add_Info('logout failed , not run')
                else:
                    self.master.Debug_Add_Info('login error')
            else:
                self.master.Debug_Add_Info('not run ???')
        else:
            self.master.Debug_Add_Info('first connect!')
# 登录
# "\x02sMN SetAccessMode 03 F4724744\x03"
# "\x02sAN SetAccessMode 1\x03"
# 设置角度分辨率
# "\x02sMN mLMPsetscancfg 9C4 1 9C4 FFFF3CB0 1C3A90\x03"
# "\x02sAN mLMPsetscancfg 0 9C4 1 9C4 FFFF3CB0 1C3A90\x03"
# 设置角度范围
# "\x02sWN LMPoutputRange 1 +5000 +450000 +1350000\x03"
# "\x02sWA LMPoutputRange\x03"
# 退出登录
# "\x02sMN Run\x03"
# "\x02sAN Run 1\x03"




