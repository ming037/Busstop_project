#!/usr/bin/python3
# -*- coding: utf-8 -*-
import threading
import sys
import schedule
import time
import requests
from bs4 import BeautifulSoup
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class TestThread(QThread):
    # 쓰레드의 커스텀 이벤트
    # 데이터 전달 시 형을 명시해야 함
    threadEvent = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__()
        self.n = 0
        self.main = parent
        self.isRun = False

    def run(self):
        while self.isRun:
            print('쓰레드 : ' + str(self.n))

            # 'threadEvent' 이벤트 발생
            # 파라미터 전달 가능(객체도 가능)
            self.threadEvent.emit(self.n)

            self.n += 1
            self.sleep(1)


class Parsing(QObject):
    threadEvent = pyqtSignal(int)

    def __init__(self, interval, getClass):
        super().__init__()

        self.interval = interval
        self.getClass = getClass
        self.end = True  # 스레드 관리용 (종료시 스레드 멈추기)



    @pyqtSlot()
    def run(self):
        url = 'http://openapi.jeonju.go.kr/jeonjubus/openApi/traffic/bus_location_busstop_infomation.do'
        key = ''
        stop_id_1 = '306101044'  # [31043] 전북대학교(농협앞)
        stop_id_2 = '306101049'  # [31048] 전북대학교(한나여성병원앞)
        self.get_bus_data(url, key, stop_id_1, 1)
        self.get_bus_data(url, key, stop_id_2, 2)
        schedule.every(self.interval).seconds.do(self.get_bus_data, url, key, stop_id_1, 1)
        schedule.every(self.interval).seconds.do(self.get_bus_data, url, key, stop_id_2, 2)


        while self.end:
            schedule.run_pending()
            time.sleep(1)

    def get_bus_data(self, url, key, stop_id, position):
        line = []
        arrival = []
        current_pass = []
        heading = []
        soon = []
        soon_index = 0
        result_numbers = []  # 결과 버스 노선 번호
        result_waiting = []  # 결과 대기시간
        result_current = []  # 결과 현재 위치
        result_heading =[]  # 결과 행선지
        soon_result = "DNPJMXRLEORSXPM"
        source_code = requests.post(url, data={'authApiKey': key, 'stopStdid': stop_id, "orderBy":"rTime", "range":"asc"})
        #http://openapi.jeonju.go.kr/jeonjubus/openApi/traffic/bus_location_busstop_infomation.do?authApiKey=DNPJMXRLEORSXPM&stopStdid=306101049&orderBy=rTime&range=asc
        plain_text = source_code.text
        soup = BeautifulSoup(plain_text, 'xml')  # source code from the website
        #  노선:6 분선:4 도착시간:2 현재위치:15 방면:8
        for link in soup.findAll("list"):
            # 노선정보
            get_line_info = link.contents[6].text
            get_subline_info = link.contents[4].text
            if get_subline_info != '0':
                get_line_info += '-'
                get_line_info += get_subline_info
            line.append(get_line_info)
            # 남은 시간 정보
            get_time_info = int(link.contents[2].text) // 60
            arrival.append(str(get_time_info)+"분")
            if get_time_info <= 3:
                soon.append(soon_index)
            soon_index += 1
            # 현재 위치 정보
            current_pass.append(link.contents[15].text)
            # 방면 정보
            get_heading_info = link.contents[8].text
            heading.append(get_heading_info[get_heading_info.find('>')+1:])

        # Set ResultData
        for index in range(0, len(line)):
            if index not in soon:
                result_numbers.append(line[index])
                result_waiting.append(arrival[index])
                result_current.append(current_pass[index])
                result_heading.append(heading[index])

        for index in range(0, len(soon)):
            soon_result += line[index]
            soon_result += ", "

        self.print_info(result_numbers,result_waiting,result_current, result_heading, soon_result, position)





class Parsing2(threading.Thread):
    def __init__(self, interval, getClass):
        super().__init__()
        self.interval = interval
        self.getClass = getClass
        self.a = 10
        self.end = True  # 스레드 관리용 (종료시 스레드 멈추기)

    def run(self):
        url = 'http://openapi.jeonju.go.kr/jeonjubus/openApi/traffic/bus_location_busstop_infomation.do'
        key = ''
        stop_id_1 = '306101044'  # [31043] 전북대학교(농협앞)
        stop_id_2 = '306101049'  # [31048] 전북대학교(한나여성병원앞)
        self.get_bus_data(url, key, stop_id_1, 1)
        self.get_bus_data(url, key, stop_id_2, 2)
        schedule.every(self.interval).seconds.do(self.get_bus_data, url, key, stop_id_1, 1)
        schedule.every(self.interval).seconds.do(self.get_bus_data, url, key, stop_id_2, 2)

        while self.end:
            schedule.run_pending()
            time.sleep(1)

    def get_bus_data(self, url, key, stop_id, position):
        line = []
        arrival = []
        current_pass = []
        heading = []
        soon = []
        soon_index = 0
        result_numbers = []  # 결과 버스 노선 번호
        result_waiting = []  # 결과 대기시간
        result_current = []  # 결과 현재 위치
        result_heading =[]  # 결과 행선지
        soon_result = ""
        source_code = requests.post(url, data={'authApiKey': key, 'stopStdid': stop_id, "orderBy":"rTime", "range":"asc"})
        #http://openapi.jeonju.go.kr/jeonjubus/openApi/traffic/bus_location_busstop_infomation.do?authApiKey=DNPJMXRLEORSXPM&stopStdid=306101049&orderBy=rTime&range=asc
        plain_text = source_code.text
        soup = BeautifulSoup(plain_text, 'xml')  # source code from the website
        #  노선:6 분선:4 도착시간:2 현재위치:15 방면:8
        for link in soup.findAll("list"):
            # 노선정보
            get_line_info = link.contents[6].text
            get_subline_info = link.contents[4].text
            if get_subline_info != '0':
                get_line_info += '-'
                get_line_info += get_subline_info
            line.append(get_line_info)
            # 남은 시간 정보
            get_time_info = int(link.contents[2].text) // 60
            arrival.append(str(get_time_info)+"분")
            if get_time_info <= 3:
                soon.append(soon_index)
            soon_index += 1
            # 현재 위치 정보
            current_pass.append(link.contents[15].text)
            # 방면 정보
            get_heading_info = link.contents[8].text
            heading.append(get_heading_info[get_heading_info.find('>')+1:])

        # Set ResultData
        for index in range(0, len(line)):
            if index not in soon:
                result_numbers.append(line[index])
                result_waiting.append(arrival[index])
                result_current.append(current_pass[index])
                result_heading.append(heading[index])

        for index in range(0, len(soon)):
            soon_result += line[index]
            soon_result += ", "

        self.print_info(result_numbers,result_waiting,result_current, result_heading, soon_result, position)

    def print_info(self, bus_numbers, waiting, current, heading, soon_info, y_pos):
        if y_pos == 1:
            for i in range(0, 11):  # len(self.getClass.numberlabels1)
                if i >= len(bus_numbers):
                    self.getClass.numberlabels1[i].setVisible(False)
                    self.getClass.waitinglabels1[i].setVisible(False)
                    self.getClass.currentlabels1[i].setVisible(False)
                    self.getClass.headinglabels1[i].setVisible(False)
                else:
                    self.getClass.numberlabels1[i].setText(bus_numbers[i])
                    self.getClass.numberlabels1[i].adjustSize()
                    self.getClass.numberlabels1[i].setVisible(True)

                    self.getClass.waitinglabels1[i].setText(waiting[i])
                    self.getClass.waitinglabels1[i].adjustSize()
                    self.getClass.waitinglabels1[i].setVisible(True)

                    self.getClass.currentlabels1[i].setText(current[i][:8])
                    self.getClass.currentlabels1[i].adjustSize()
                    self.getClass.currentlabels1[i].setVisible(True)

                    self.getClass.headinglabels1[i].setText(heading[i][:8])
                    self.getClass.headinglabels1[i].adjustSize()
                    self.getClass.headinglabels1[i].setVisible(True)

            self.getClass.soon_arrival1.setText(soon_info)
            self.getClass.soon_arrival1.adjustSize()
        else:
            for i in range(0, 11):  # len(self.getClass.numberlabels2)
                if i >= len(bus_numbers):
                    self.getClass.numberlabels2[i].setVisible(False)
                    self.getClass.waitinglabels2[i].setVisible(False)
                    self.getClass.currentlabels2[i].setVisible(False)
                    self.getClass.headinglabels2[i].setVisible(False)
                else:
                    self.getClass.numberlabels2[i].setText(bus_numbers[i])
                    self.getClass.numberlabels2[i].adjustSize()
                    self.getClass.numberlabels2[i].setVisible(True)

                    self.getClass.waitinglabels2[i].setText(waiting[i])
                    self.getClass.waitinglabels2[i].adjustSize()
                    self.getClass.waitinglabels2[i].setVisible(True)

                    self.getClass.currentlabels2[i].setText(current[i][:8])
                    self.getClass.currentlabels2[i].adjustSize()
                    self.getClass.currentlabels2[i].setVisible(True)

                    self.getClass.headinglabels2[i].setText(heading[i][:8])
                    self.getClass.headinglabels2[i].adjustSize()
                    self.getClass.headinglabels2[i].setVisible(True)
            self.getClass.soon_arrival2.setText(soon_info)
            self.getClass.soon_arrival2.adjustSize()

    def stop_thread(self):
        self.end = False


class StartApp(QWidget):
    def __init__(self):
        super().__init__()

        self.namelabel1 = QLabel(self)  # 정류장 이름
        self.namelabel2 = QLabel(self)
        self.labelgroup = []
        self.labelgroup2 = []
        self.numberlabels1 = []  # 노선 이름
        self.numberlabels2 = []
        self.waitinglabels1 = []  # 대기 시간
        self.waitinglabels2 = []
        self.currentlabels1 = []  # 현재 위치
        self.currentlabels2 = []
        self.headinglabels1 = []  # 행선지
        self.headinglabels2 = []
        self.soon_arrival1 = QLabel(self)
        self.soon_arrival2 = QLabel(self)

        self.initUI()
        self.parse = Parsing(10, self)
        self.parse.start()

    def initUI(self):
        font = QFont()
        font.setFamily("맑은 고딕")
        font.setBold(True)
        font.setPointSize(30)

        numberfont = QFont()
        numberfont.setFamily("맑은 고딕")
        numberfont.setBold(True)

        numberfont.setPointSize(35)

        self.namelabel1.move(190, 70)
        self.namelabel2.move(1135, 70)
        self.namelabel1.setFont(font)
        self.namelabel2.setFont(font)
        self.namelabel1.setText("[31043] 전북대학교(농협앞)")
        self.namelabel2.setText("[31048] 전북대학교(한나여성병원앞)")
        # Initialize
        for i in range(1,12):
            self.numberlabels1.append(QLabel(self))
            self.numberlabels2.append(QLabel(self))
            self.waitinglabels1.append(QLabel(self))
            self.waitinglabels2.append(QLabel(self))
            self.currentlabels1.append(QLabel(self))
            self.currentlabels2.append(QLabel(self))
            self.headinglabels1.append(QLabel(self))
            self.headinglabels2.append(QLabel(self))
        # 버스 번호
        inter = 0
        for lbl in self.numberlabels1:
            lbl.move(50, 215 + inter)
            lbl.setFont(numberfont)
            lbl.setStyleSheet("color:rgb(0,71,193);")
            lbl.setVisible(False)
            inter += 62
        inter = 0
        for lbl in self.numberlabels2:
            lbl.move(1000, 215 + inter)
            lbl.setFont(numberfont)
            lbl.setStyleSheet("color:rgb(0,71,193);")
            lbl.setVisible(False)
            inter += 62
        # 대기 시간
        inter = 0
        for lbl in self.waitinglabels1:
            lbl.move(160, 220 + inter)
            lbl.setFont(font)
            lbl.setStyleSheet("color:rgb(255,100,0);")
            inter += 62
            lbl.setVisible(False)
        inter = 0
        for lbl in self.waitinglabels2:
            lbl.move(1110, 220 + inter)
            lbl.setFont(font)
            lbl.setStyleSheet("color:rgb(255,100,0);")
            inter += 62
            lbl.setVisible(False)
        # 현재 위치
        inter = 0
        for lbl in self.currentlabels1:
            lbl.move(290, 220 + inter)
            lbl.setFont(font)
            inter += 62
            lbl.setVisible(False)

        inter = 0
        for lbl in self.currentlabels2:
            lbl.move(1250, 220 + inter)
            lbl.setFont(font)
            inter += 62
            lbl.setVisible(False)
        # 행선지
        inter = 0
        for lbl in self.headinglabels1:
            lbl.move(650, 220 + inter)
            lbl.setFont(font)
            inter += 62
            lbl.setVisible(False)

        inter = 0
        for lbl in self.headinglabels2:
            lbl.move(1600, 220 + inter)
            lbl.setFont(font)
            inter += 62
            lbl.setVisible(False)
        # 잠시 후 도착
        self.soon_arrival1.move(60, 963)
        self.soon_arrival2.move(1010, 963)
        self.soon_arrival1.setFont(numberfont)
        self.soon_arrival2.setFont(numberfont)
        self.soon_arrival1.setStyleSheet("color:rgb(42,147,0);")
        self.soon_arrival2.setStyleSheet("color:rgb(42,147,0);")
        self.soon_arrival1.setText("")
        self.soon_arrival2.setText("")
        # 배경화면
        self.showFullScreen()
        oimage = QImage("background.png")
        simage = oimage.scaled(QSize(self.width(), self.height()))
        palette = QPalette()
        palette.setBrush(10, QBrush(simage))
        self.setPalette(palette)

        self.setWindowTitle('MyBusStop')
        self.show()

    def keyPressEvent(self, QKeyEvent):
        if QKeyEvent.key() == Qt.Key_Escape:
            self.parse.stop_thread()
            sys.exit()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = StartApp()
    sys.exit(app.exec_())
