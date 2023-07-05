import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QLineEdit, QLabel, QFileDialog
from PyQt5.QtCore import pyqtSlot

from PyQt5.QtCore import QSize
from PyQt5 import QtCore

from pymodbus.client.sync import ModbusTcpClient
from pymodbus.exceptions import ConnectionException
import struct
import os
from datetime import datetime
import csv
from multiprocessing import Process,freeze_support
from pathlib import Path


def fun(ip_ok,cur_dirr):
    q=1
    close_bool=0
    now = datetime.now()
    datee_ini=now.strftime("%m-%d-%Y")
    cur_head_csv=1
    ris_edge=False
    while q==1 and close_bool==0:
        now = datetime.now()
        datee=now.strftime("%m-%d-%Y")
        
        client = ModbusTcpClient(ip_ok, port=502, timeout=3)
        client.connect()
        
        if client.connect()!=False:       
            try:
                input_sta_add=1
                input_sta_read=client.read_discrete_inputs(address = 42 ,count =input_sta_add,unit=1)
                try:
                    input_sta_reg=input_sta_read.bits                 
                except AttributeError:
                    input_sta_reg=[""]

                if ris_edge==True and input_sta_reg[0]==False:
                    ris_edge=False
                
                if input_sta_reg[0]==True and ris_edge==False:              
                    ris_edge=True
                    now = datetime.now()
                    date_time = now.strftime("%m/%d/%Y %H:%M:%S")
                    input_add=108
                    
                    input_read=client.read_input_registers(address = 0 ,count =input_add,unit=1)
                    input_reg=input_read.registers
                    

                    if len(input_reg)!=0:                        
                        input_32f_list=[]               
                        for i in range(0,len(input_reg),2):
                            print(i)
                            b=input_reg[i]
                            try:
                                a=input_reg[i+1]
                            except IndexError:
                                a=0
                                
                            if a==0:
                                input_32f=float(0)
                                input_32f_list.append(input_32f)
                          
                            else:
                                input_32f=struct.unpack('!f', bytes.fromhex('{0:04x}'.format(a) + '{0:04x}'.format(b)))
                                input_32f_list.append(round(input_32f[0],2))
                            
                            
                        input_32f_list.insert(0,date_time)
                
                        header_name=["DATE","Point1_Avg","Point2_Avg","Point3_Avg","Point4_Avg","Point5_Avg","Point6_Avg","Point7_Avg","Point8_Avg","Point9_Avg","Point10_Avg","Area1_Max","Area1_Min","Area1_Avg","Area1_TD","Area2_Max","Area2_Min","Area2_Avg","Area2_TD","Area3_Max","Area3_Min","Area3_Avg","Area3_TD","Area4_Max","Area4_Min","Area4_Avg","Area4_TD","Area5_Max","Area5_Min","Area5_Avg","Area5_TD","Area6_Max","Area6_Min","Area6_Avg","Area6_TD","Area7_Max","Area7_Min","Area7_Avg","Area7_TD","Area8_Max","Area8_Min","Area8_Avg","Area8_TD","Area9_Max","Area9_Min","Area9_Avg","Area9_TD","Area10_Max","Area10_Min","Area10_Avg","Area10_TD","Line1_Max","Line1_Min","Line1_Avg","Chip_Temp"]
                        input_32f_val=[]
                        input_header_name=[]
                        for i in range(len(input_32f_list)):
                            if input_32f_list[i]==-273.15 or input_32f_list[i]==0.0:                            
                                continue
                                                        
                            input_header_name.append(header_name[i])
                            input_32f_val.append(input_32f_list[i])

                        
                    try:                                             
                        if datee_ini!=datee and cur_head_csv==0:                           
                            with open(cur_dirr+"\\"+ip_ok+"_"+datee+'.csv', 'a+', newline='', encoding = "UTF-8") as file:                              
                                  write = csv.writer(file)       
                                  write.writerows([input_header_name])
                                  cur_head_csv=0
                                  datee_ini=datee
                         
                        if cur_head_csv==1 :                          
                            with open(cur_dirr+"\\"+ip_ok+"_"+datee+'.csv', 'a+', newline='', encoding = "UTF-8") as file:                              
                                  write = csv.writer(file)       
                                  write.writerows([input_header_name])
                                  cur_head_csv=0
                                                           
                    except PermissionError:
                        print("Please close the file if it is open") 
                    
                    
                    try:
                        with open(cur_dirr+"\\"+ip_ok+"_"+datee+'.csv', 'a+', newline='', encoding = "UTF-8") as file:                              
                              write = csv.writer(file)       
                              write.writerows([input_32f_val])
                                                           
                    except PermissionError:
                        print("Please close the file if it is open")    
                      
                client.close()
                
            except ConnectionException:           
                client.close()

            
class App(QMainWindow):  
    def __init__(self):
        super().__init__()
        self.title = 'example_report'
        self.left = 600
        self.top = 300
        self.width = 400
        self.height = 400
        self.initUI()
    
    def initUI(self):
        directory= "C:\REPORT"
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        
        self.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, False)
        
        self.label_1 = QLabel("IP 1 :", self)
        self.label_1.move(20, 110)
        self.textbox1 = QLineEdit(self)
        self.textbox1.move(60, 110)
        self.textbox1.resize(150,30)
        
        
        self.label_2 = QLabel("IP 2 :", self)
        self.label_2.move(20, 150)
        self.textbox2 = QLineEdit(self)
        self.textbox2.move(60, 150)
        self.textbox2.resize(150,30)
        
        self.label_3 = QLabel("IP 3 :", self)
        self.label_3.move(20, 190)
        self.textbox3 = QLineEdit(self)
        self.textbox3.move(60, 190)
        self.textbox3.resize(150,30)
        
        self.label_4 = QLabel("IP 4 :", self)
        self.label_4.move(20, 230)
        self.textbox4 = QLineEdit(self)
        self.textbox4.move(60, 230)
        self.textbox4.resize(150,30)
        
        self.label_5 = QLabel("IP 5 :", self)
        self.label_5.move(20, 270)
        self.textbox5 = QLineEdit(self)
        self.textbox5.move(60, 270)
        self.textbox5.resize(150,30) 
        
        self.label_6 = QLabel("IP 6 :", self)
        self.label_6.move(20, 310)
        self.textbox6 = QLineEdit(self)
        self.textbox6.move(60, 310)
        self.textbox6.resize(150,30)
        
        self.label_7 = QLabel("IP 7 :", self)
        self.label_7.move(20, 350)
        self.textbox7 = QLineEdit(self)
        self.textbox7.move(60, 350)
        self.textbox7.resize(150,30)
        
        self.label_8 = QLabel("IP 8 :", self)
        self.label_8.move(20, 390)
        self.textbox8 = QLineEdit(self)
        self.textbox8.move(60, 390)
        self.textbox8.resize(150,30)
        
        
        self.label_9 = QLabel("IP 9 :", self)
        self.label_9.move(250, 110)
        self.textbox9 = QLineEdit(self)
        self.textbox9.move(300, 110)
        self.textbox9.resize(150,30) 
        
        self.label_10 = QLabel("IP 10 :", self)
        self.label_10.move(250, 150)
        self.textbox10 = QLineEdit(self)
        self.textbox10.move(300, 150)
        self.textbox10.resize(150,30)
        
        self.label_11 = QLabel("IP 11 :", self)
        self.label_11.move(250, 190)
        self.textbox11 = QLineEdit(self)
        self.textbox11.move(300, 190)
        self.textbox11.resize(150,30)
        
        self.label_12 = QLabel("IP 12 :", self)
        self.label_12.move(250, 230)
        self.textbox12 = QLineEdit(self)
        self.textbox12.move(300, 230)
        self.textbox12.resize(150,30)
        
        self.label_13 = QLabel("IP 13 :", self)
        self.label_13.move(250, 270)
        self.textbox13 = QLineEdit(self)
        self.textbox13.move(300, 270)
        self.textbox13.resize(150,30)
        
        self.label_14 = QLabel("IP 14 :", self)
        self.label_14.move(250, 310)
        self.textbox14 = QLineEdit(self)
        self.textbox14.move(300, 310)
        self.textbox14.resize(150,30)
        
        self.label_15 = QLabel("IP 15 :", self)
        self.label_15.move(250, 350)
        self.textbox15 = QLineEdit(self)
        self.textbox15.move(300, 350)
        self.textbox15.resize(150,30)
        
        self.label_16 = QLabel("IP 16 :", self)
        self.label_16.move(250, 390)
        self.textbox16 = QLineEdit(self)
        self.textbox16.move(300, 390)
        self.textbox16.resize(150,30)
        
        self.label_a = QLabel("Please back up the data regularly to avoid the disk being too full!!!", self)
        self.label_a.setStyleSheet("font-size: 18px; color: red")
        self.label_a.resize(500, 40)
        self.label_a.move(10, 10)
        self.label_p = QLabel("Path :", self)
        self.label_p.move(20, 60)
        
        self.dir_btn = QPushButton('Browse',self)
        self.dir_btn.move(320,60)
        self.dir_btn.clicked.connect(self.open_dir_dialog)
        self.dir_name_edit = QLineEdit(self)
        self.dir_name_edit.move(60, 60)
        self.dir_name_edit.resize(250,30)
        self.dir_name_edit.setText(str(directory))
        self.cur_dir=str(directory)
        
        self.button = QPushButton('Confirm', self)
        self.button.move(100,450)
        
        self.button2 = QPushButton('Close', self)
        self.button2.move(280,450)

        self.button.clicked.connect(self.on_click)
        self.button2.clicked.connect(self.click_close)
        self.setFixedSize(QSize(485, 520))
    
    
    @pyqtSlot()
    def open_dir_dialog(self):
        dir_name = QFileDialog.getExistingDirectory(self, "Select a Directory")
        if dir_name:
            path = Path(dir_name)
            self.dir_name_edit.setText(str(path))
                     
    def click_close(self):
        global close_bool
        close_bool=1
        try:
            self.p1.terminate()
            self.p2.terminate()
            self.p3.terminate()
            self.p4.terminate()
            self.p5.terminate()
            self.p6.terminate()
            self.p7.terminate()
            self.p8.terminate()
            self.p9.terminate()
            self.p10.terminate()
            self.p11.terminate()
            self.p12.terminate()
            self.p13.terminate()
            self.p14.terminate()
            self.p15.terminate()
            self.p16.terminate()
        except AttributeError:
            self.close()
        self.close()
    
    def on_click(self):
        
        try:
            #os.mkdir(r"D:\reporrr")
            self.cur_dir=self.dir_name_edit.text()
            print(self.cur_dir)
            os.makedirs(self.cur_dir)

        except FileExistsError:
            pass
        
   
        self.dir_btn.setEnabled(False)     
        self.button.setEnabled(False)
        self.dir_name_edit.setEnabled(False)
        self.textbox1.setEnabled(False)
        self.textbox2.setEnabled(False)
        self.textbox3.setEnabled(False)
        self.textbox4.setEnabled(False)
        self.textbox5.setEnabled(False)
        self.textbox6.setEnabled(False)
        self.textbox7.setEnabled(False)
        self.textbox8.setEnabled(False)
        self.textbox9.setEnabled(False)
        self.textbox10.setEnabled(False)
        self.textbox11.setEnabled(False)
        self.textbox12.setEnabled(False)
        self.textbox13.setEnabled(False)
        self.textbox14.setEnabled(False)
        self.textbox15.setEnabled(False)
        self.textbox16.setEnabled(False)
        
        textboxValue1 = self.textbox1.text()
        textboxValue2 = self.textbox2.text()
        textboxValue3 = self.textbox3.text()
        textboxValue4 = self.textbox4.text()
        textboxValue5 = self.textbox5.text()
        textboxValue6 = self.textbox6.text()
        textboxValue7 = self.textbox7.text()
        textboxValue8 = self.textbox8.text()
        textboxValue9 = self.textbox9.text()
        textboxValue10 = self.textbox10.text()
        textboxValue11 = self.textbox11.text()
        textboxValue12 = self.textbox12.text()
        textboxValue13 = self.textbox13.text()
        textboxValue14 = self.textbox14.text()
        textboxValue15 = self.textbox15.text()
        textboxValue16 = self.textbox16.text()
        
        self.p1 = Process(target=fun, args=[textboxValue1,self.cur_dir])
        self.p2 = Process(target=fun, args=[textboxValue2,self.cur_dir])
        self.p3 = Process(target=fun, args=[textboxValue3,self.cur_dir])
        self.p4 = Process(target=fun, args=[textboxValue4,self.cur_dir])
        self.p5 = Process(target=fun, args=[textboxValue5,self.cur_dir])
        self.p6 = Process(target=fun, args=[textboxValue6,self.cur_dir])
        self.p7 = Process(target=fun, args=[textboxValue7,self.cur_dir])
        self.p8 = Process(target=fun, args=[textboxValue8,self.cur_dir])
        self.p9 = Process(target=fun, args=[textboxValue9,self.cur_dir])
        self.p10 = Process(target=fun, args=[textboxValue10,self.cur_dir])
        self.p11 = Process(target=fun, args=[textboxValue11,self.cur_dir])
        self.p12 = Process(target=fun, args=[textboxValue12,self.cur_dir])
        self.p13 = Process(target=fun, args=[textboxValue13,self.cur_dir])
        self.p14 = Process(target=fun, args=[textboxValue14,self.cur_dir])
        self.p15 = Process(target=fun, args=[textboxValue15,self.cur_dir])
        self.p16 = Process(target=fun, args=[textboxValue16,self.cur_dir])
        
        
        self.p1.start()
        self.p2.start()
        self.p3.start()
        self.p4.start()
        self.p5.start()
        self.p6.start()
        self.p7.start()
        self.p8.start()
        self.p9.start()
        self.p10.start()
        self.p11.start()
        self.p12.start()
        self.p13.start()
        self.p14.start()
        self.p15.start()
        self.p16.start()
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    freeze_support()
    ex = App()
    ex.show()
    sys.exit(app.exec_())
