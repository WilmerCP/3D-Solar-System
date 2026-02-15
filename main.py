from PyQt5 import QtCore, QtGui, QtWidgets
from interface import *
from glwidget import SolarSystemGL
from PyQt5.QtWidgets import QShortcut
from PyQt5.QtGui import QKeySequence, QSurfaceFormat

format = QSurfaceFormat()
format.setSamples(4)  # 4x MSAA
QSurfaceFormat.setDefaultFormat(format)

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
        self.previous_page = self.ui.start_page

        pixmap = QtGui.QPixmap("textures/ibu.png") 
        self.ui.logo_label.setPixmap(pixmap)
        self.ui.logo_label.setScaledContents(False)

        self.esc_shortcut = QShortcut(QKeySequence("Esc"), self.ui.controls_page)
        self.esc_shortcut.activated.connect(lambda: self.change_page(self.previous_page))
        self.c_shortcut = QShortcut(QKeySequence("C"), self.ui.controls_page)
        self.c_shortcut.activated.connect(lambda: self.change_page(self.previous_page))

        self.connect_buttons()

    def connect_buttons(self):
        self.ui.start_button.clicked.connect(lambda: self.change_page(self.ui.animation_page))
        self.ui.openGLWidget.back_to_menu.connect(lambda: self.change_page(self.ui.start_page))
        self.ui.openGLWidget.back_to_controls.connect(lambda: self.change_page(self.ui.controls_page))
        self.ui.controls_button.clicked.connect(lambda: self.change_page(self.ui.controls_page))

    def change_page(self,widget):
        self.previous_page = self.ui.stackedWidget.currentWidget()
        self.ui.stackedWidget.setCurrentWidget(widget)


window = Window("Solar System Simulation")

window.show()
app.exec_()