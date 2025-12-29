from PyQt5 import QtCore, QtGui, QtWidgets
from interface import *
from glwidget import SolarSystemGL

app = QtWidgets.QApplication([])

#Main Window Class

class Window(QtWidgets.QMainWindow):

    #constructor
    def __init__(self,title):

        super(Window,self).__init__()
        
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.change_page(self.ui.start_page)
        self.setWindowTitle(title)


        self.connect_buttons()

    def connect_buttons(self):
        self.ui.start_button.clicked.connect(lambda: self.change_page(self.ui.animation_page))

    def change_page(self,widget):
        
        self.ui.stackedWidget.setCurrentWidget(widget)


window = Window("Solar System Simulation")

window.show()
app.exec_()