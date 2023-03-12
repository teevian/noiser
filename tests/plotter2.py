import sys
import os
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QSize, QTimer
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem
import pyqtgraph as pg
from pyqtgraph import ViewBox
import numpy as np
from random import randint
import time

class MyWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("GUI Arduíno")
        self.setMinimumSize(QSize(1000,600))
        self.setStyleSheet("background-color: grey;")
        self.i = 0

        self.plot = pg.PlotWidget()
        self.plot.getViewBox().setMouseEnabled(y=False)

        self.flag = 0
        self.t = np.zeros(600)
        self.V = np.zeros(600)
        self.ma = np.zeros(600)
        self.t0 = time.time()
        self.current_time = self.t0
        self.paused_time = 0
        self.pen = pg.mkPen(color=(255, 0, 0))

        self.plot.setTitle("Real time data from Arduino")
        self.plot.setLabel('left', 'Tensão (V)')
        self.plot.setLabel('bottom', 'Tempo (s)')

        #Layout com os botões 

        self.button_widget = QtWidgets.QWidget(self)
        self.button_layout = QtWidgets.QHBoxLayout(self.button_widget)

        self.button1 = QtWidgets.QPushButton('Pause', self.button_widget)
        self.button1.clicked.connect(self.pause_resume)
        self.button1.setCheckable(True)
        self.button_layout.addWidget(self.button1)

        self.button2 = QtWidgets.QPushButton('Clear', self.button_widget)
        self.button2.clicked.connect(self.update_plot_data)
        self.button2.setCheckable(True)
        self.button_layout.addWidget(self.button2)

        self.button3 = QtWidgets.QPushButton('Moving Avarage: OFF', self.button_widget)
        self.button3.clicked.connect(self.ma_check)
        self.button3.setCheckable(True)
        self.button_layout.addWidget(self.button3)

        self.button4 = QtWidgets.QPushButton('Center', self.button_widget)
        self.button4.clicked.connect(self.center_graph)
        self.button4.setCheckable(True)
        self.button_layout.addWidget(self.button4)

        self.label1 = QtWidgets.QLabel("Sinal: Não Estabilizado", self.button_widget)
        self.button_layout.addWidget(self.label1)

        #Tabela com os valores

        self.table = QTableWidget()
        self.table.setRowCount(1)
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Time (s)", "Voltage (V)"])

        #Label

        self.label_text = QtWidgets.QLabel("Valores atuais:")
        self.t_value = 0
        self.V_value = 0
        self.label_text.setText("t = " + str(self.t_value) + "\nV = " + str(self.V_value))
        


        #Layout com o plot

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.label_text)
        layout1 = QtWidgets.QHBoxLayout(self)
        layout1.addWidget(self.plot)
        layout1.addWidget(self.table)
        layout.addLayout(layout1)
        layout.addWidget(self.button_widget)

        #Update do gráfico

        self.timer = QtCore.QTimer()
        self.timer.setInterval(50)
        self.timer.timeout.connect(self.update_plot_data)
        self.timer.start()

        

    def update_plot_data(self):
        
        self.current_time = time.time() - self.t0
        color = "r"

        self.i = self.i + 1 

        self.t[self.i] = self.current_time
        self.V[self.i] = randint(0, 5000)*0.001

        last_10 = self.V[self.i-10:self.i]
        threshold = 0.01

        if self.current_time <= 10:

            if np.std(last_10) < threshold:
                
                color = "b"
                self.label1.setText("Sinal Estabilizado")
            else:
                color = "r"
                self.label1.setText("Sinal Não Estabilizado")

            self.data_line =  self.plot.plot(self.t[:self.i], self.V[:self.i], pen=color)

            if self.flag == 1 and self.i >= 3:

                self.ma[self.i] = (self.V[self.i -3] + self.V[self.i -2] + self.V[self.i -1] + self.V[self.i] + self.V[self.i+1] + self.V[self.i+2] + self.V[self.i+3])/7.
                self.data_line1 = self.plot.plot(self.t[:self.i], self.ma[:self.i] , pen = "g")

            self.plot.setXRange(0, 10)
        elif self.current_time > 10 and self.current_time <= 30:

            if np.std(last_10) < threshold:
                
                color = "b"
                self.label1.setText("Sinal Estabilizado")
            else:
                color = "r"
                self.label1.setText("Sinal Não Estabilizado")
                
            self.data_line =  self.plot.plot(self.t[:self.i], self.V[:self.i], pen=color)
            
            if self.flag == 1:

                self.ma[self.i] = (self.V[self.i -3] + self.V[self.i -2] + self.V[self.i -1] + self.V[self.i] + self.V[self.i+1] + self.V[self.i+2] + self.V[self.i+3])/7.
                self.data_line1 = self.plot.plot(self.t[:self.i], self.ma[:self.i] , pen = "g")
            self.plot.setXRange(self.current_time - 10, self.current_time)
        else:
            self.timer.stop()

        self.label_text.setText("t = " + str(round(self.t[self.i], 4)) + "\nV = " + str(round(self.V[self.i], 4)))
        self.table.setRowCount(self.i)
        for r in range(self.i):
            self.table.setItem(r, 0, QTableWidgetItem(str(round(self.t[r], 4))))
            self.table.setItem(r, 1, QTableWidgetItem(str(round(self.V[r], 4))))


        if self.button2.isChecked():

            self.t = np.zeros(600)
            self.V = np.zeros(600)

            self.t0 = time.time()
            self.current_time = self.t0
            self.plot.setXRange(0, 10)
            self.i = 0

            self.plot.clear()

            self.button2.setChecked(False)


    def pause_resume(self):

        if self.button1.isChecked():

            self.timer.stop()
            self.button1.setText("Resume")
            self.paused_time = self.current_time
        else:

            self.timer.start(50)
            self.button1.setText("Pause")
            self.t0 = time.time() - self.paused_time 
    
    def ma_check(self):
        
        if self.button3.isChecked():

            self.flag = 1
            self.button3.setText("Moving Avarage: ON")
            
        else:

            self.flag = 0
            self.button3.setText("Moving Avarage: OFF")

    def center_graph(self):

        if self.button4.isChecked():

            if self.current_time <= 10:

                self.plot.setXRange(0, 10)

            elif self.current_time > 10:

                self.plot.setXRange(self.current_time - 10, self.current_time)
                self.button4.setChecked(False)
  
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    win = MyWindow()
    win.show()
    sys.exit(app.exec_())