import PySide2
from PySide2.QtWidgets import QApplication, QMessageBox,QFileDialog
from PySide2.QtUiTools import QUiLoader
import os
import sys
import PIL.Image as pil
import socket
from io import BytesIO
import time

class Stats:
    def __init__(self):
        # 从文件中加载UI定义

        # 从 UI 定义中动态 创建一个相应的窗口对象
        # 注意：里面的控件对象也成为窗口对象的属性了
        # 比如 self.ui.button , self.ui.textEdit
        self.ui = QUiLoader().load('tcp_client.ui')
        self.connectable = False
        self.ui.Connectable.clicked.connect(self.connect)
        self.ui.Video_search.clicked.connect(self.openFileNameDialog)
        
    def connect(self):
        if self.connectable == False:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            PORT = int(self.ui.Port.text())
            HOST = "{}.{}.{}.{}".format(self.ui.Ip_1.text(),self.ui.Ip_2.text(),self.ui.Ip_3.text(),self.ui.Ip_4.text())
            self.sock.connect((HOST,PORT))
            self.connectable = True
            self.ui.Connectable.setText("断开")
        else:
            self.sock.close()
            self.connectable = False
            self.ui.Connectable.setText("连接")

    def openFileNameDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        self.fileName, _ = QFileDialog.getOpenFileName(self.ui, "QFileDialog.getOpenFileName()", "","Video files (*.mp4 *.rmvb *.avi *.rm)", options=options)
        self.ui.Video_path.setText(self.fileName)

    def send(self):
        if self.QButtonGroup.checkedButton().text()=="图像(一)":
            
            head = bytearray(b'\xaa\xfe')
            end = bytearray(b'\x55\xee')
            Obstacle = 12312.15435
            int_Obstacle = int(Obstacle*100)

            # PIL转二进制
            # im.tobytes()
            bytesIO = BytesIO()
            im.save(bytesIO, format='JPEG')
            content = bytearray(b'\x01')+bytesIO.getvalue()+bytearray(b'\x01')+bytearray(int_Obstacle.to_bytes(4, byteorder='little'))*10

            datalen = len(content)
            datalen = bytearray(datalen.to_bytes(4, byteorder='little'))

            alldata = head + datalen + content + end
            self.sock.sendall(alldata)
            # time.sleep(2)

        else:
            pass


        QMessageBox.about(self.ui,
                    '统计结果',
                    f'''薪资20000 以上的有：\n{salary_above_20k}
                    \n薪资20000 以下的有：\n{salary_below_20k}'''
                    )

if __name__=="__main__":
    dirname = os.path.dirname(PySide2.__file__)
    plugin_path = os.path.join(dirname, 'plugins', 'platforms')
    os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path
    app = QApplication(sys.argv)
    stats = Stats()
    stats.ui.show()
    app.exec_()