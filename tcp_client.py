# import PySide2
from PySide2.QtWidgets import QApplication, QOpenGLWidget,QFileDialog
from PySide2.QtUiTools import QUiLoader
from PySide2.QtCore import Signal,QObject
# import os
# import sys
import socket
import time
from threading import Thread
import cv2


# 自定义信号源对象类型，一定要继承自 QObject
class MySignals(QObject):

    # 定义一种信号，两个参数 类型分别是： QTextBrowser 和 字符串
    # 调用 emit方法 发信号时，传入参数 必须是这里指定的 参数类型
    # text_print = Signal(QTextBrowser,str)

    # 还可以定义其他种类的信号
    update_table = Signal(str)


class Stats:
    def __init__(self):
        # 从文件中加载UI定义

        # 从 UI 定义中动态 创建一个相应的窗口对象
        # 注意：里面的控件对象也成为窗口对象的属性了
        # 比如 self.ui.button , self.ui.textEdit
        self.ui = QUiLoader().load('tcp_client.ui')
        self.connectable = False
        self.sending = False
        self.terminate = False
        self.Obstacles = [self.ui.Obstacle_1,
            self.ui.Obstacle_2,
            self.ui.Obstacle_3,
            self.ui.Obstacle_4,
            self.ui.Obstacle_5,
            self.ui.Obstacle_6,
            self.ui.Obstacle_7,
            self.ui.Obstacle_8,
            self.ui.Obstacle_9,
            self.ui.Obstacle_10]
        self.ui.Loop_send.setEnabled(False)
        self.ui.Connectable.clicked.connect(self.connect)
        self.ui.Video_search.clicked.connect(self.openFileNameDialog)
        self.ui.Loop_send.clicked.connect(self.send)
        self.ui.buttonGroup.buttonClicked.connect(self.choose1or2)
        

    def choose1or2(self):
        if self.ui.buttonGroup.checkedButton().text()=="图像(一)":
            for Obstacle in self.Obstacles:
                Obstacle.setEnabled(True)
        elif self.ui.buttonGroup.checkedButton().text()=="图像(二)":
            for Obstacle in self.Obstacles:
                Obstacle.setEnabled(False)        
            

    def connect(self):
        if self.connectable == False:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            PORT = int(self.ui.Port.text())
            HOST = "{}.{}.{}.{}".format(self.ui.Ip_1.text(),self.ui.Ip_2.text(),self.ui.Ip_3.text(),self.ui.Ip_4.text())
            self.sock.connect((HOST,PORT))
            self.connectable = True
            self.ui.Connectable.setText("断开")
            self.ui.Loop_send.setEnabled(True)
        else:
            self.sock.close()
            self.connectable = False
            self.ui.Connectable.setText("连接")
            self.ui.Loop_send.setEnabled(False)

    def openFileNameDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        self.fileName, _ = QFileDialog.getOpenFileName(self.ui, \
            "QFileDialog.getOpenFileName()", "","Video files (*.mp4 *.rmvb *.avi *.rm)", options=options)
        self.ui.Video_path.setText(self.fileName)

    def send(self):
        def threadFunc():
            caps = cv2.VideoCapture(self.fileName)
            while True:
                if self.terminate:
                    self.terminate = False
                    break
                ret, frame = caps.read()
                head = bytearray(b'\xaa\xfe')
                end = bytearray(b'\x55\xee')            
                if ret:
                    _, encoded_image = cv2.imencode(".jpg", frame)
                    if self.ui.buttonGroup.checkedButton().text()=="图像(一)":
                        Obstacles = bytearray(b'')
                        for obs in self.Obstacles:
                            Obstacles += bytearray(int(float(obs.text())*100).to_bytes(4, byteorder='big',signed=True))
                        content = bytearray(b'\x01')+encoded_image.tobytes()+bytearray(b'\x02')+Obstacles
                        
                        datalen = len(content)
                        datalen = bytearray(datalen.to_bytes(4, byteorder='big'))

                        alldata = head + datalen + content + end
                    elif self.ui.buttonGroup.checkedButton().text()=="图像(二)":
                        content = bytearray(b'\x03')+encoded_image.tobytes()
                        datalen = len(content)
                        datalen = bytearray(datalen.to_bytes(4, byteorder='big'))
                        alldata = head + datalen + content + end                    
                self.sock.sendall(alldata)
                time.sleep(0.001*int(self.ui.Sleep.text()))
        if not self.sending:
            self.thread = Thread(target = threadFunc)
            self.thread.start()
            self.sending = True
            self.ui.Loop_send.setText("停止")
            self.ui.Connectable.setEnabled(False)
        else:
            self.terminate = True
            self.sending = False
            self.ui.Loop_send.setText("发送")
            self.ui.Connectable.setEnabled(True)



if __name__=="__main__":
    # dirname = os.path.dirname(PySide2.__file__)
    # plugin_path = os.path.join(dirname, 'plugins', 'platforms')
    # os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path
    # print(plugin_path)
    app = QApplication([])
    stats = Stats()
    stats.ui.show()
    app.exec_()