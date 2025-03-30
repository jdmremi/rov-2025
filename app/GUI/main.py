import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLineEdit, 
                             QPushButton, QLabel, QGroupBox, 
                             QRadioButton, QGridLayout, QSlider,
                             QVBoxLayout, QWidget)
from PyQt5.QtCore import Qt

# MainWindow Will Show Full Camera Display For Now

# Need toggle that shows if button is connected

# For now thruster coontrol is a slider
    # In future will go to joystick if button clicked
    


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(700, 300, 500, 500)
        
        # All for controller status
        self.controller_is_connected = False  # Start with Not Detected
        self.controller_detected = QPushButton("Controller Not Detected", self)
        
        # All for thruster status
        
        self.grid = QGridLayout()

        # Create a central widget and apply the layout
        self.central_widget = QWidget()


        
        self.initUI()

    def initUI(self):
        self.controller_detected.setStyleSheet("font-size : 25px;"
                                     "font-family: Arial")
        self.controller_detected.clicked.connect(self.controller_status)
        
        
        self.central_widget.setLayout(self.grid)
        self.setCentralWidget(self.central_widget)
        
        self.grid.addWidget(self.controller_detected, 0, 0)
        self.grid.addWidget(self.initThursterControls(), 2, 0)




    def initThursterControls(self):
        groupBox = QGroupBox("Slider Example")

        radio1 = QRadioButton("&Radio horizontal slider")
        


        slider = QSlider(Qt.Horizontal)
        slider.setFocusPolicy(Qt.StrongFocus)
        slider.setTickPosition(QSlider.TicksBothSides)
        slider.setTickInterval(10)
        slider.setSingleStep(1)

        radio1.setChecked(True)

        vbox = QVBoxLayout()
        vbox.addWidget(radio1)
        vbox.addWidget(slider)
        vbox.addStretch(1)
        groupBox.setLayout(vbox)

        return groupBox
    
    def motor_controlPanel(self):
        pass
    
    def drift_stabilization(self):
        pass
       
    def take_screenshot(self):
        pass
        
    def switch_to_waypoint(self):
        pass
    
    def read_from_sensors(self):
        pass
        
        
    def controller_status(self):
        self.controller_is_connected = not self.controller_is_connected
        if self.controller_is_connected:
            self.controller_detected.setText("Controller Detected")
            self.controller_detected.setStyleSheet(
                "font-size: 25px; font-family: Arial; background-color: green; color: white;")
        else:
            self.controller_detected.setText("Controller Not Detected")
            self.controller_detected.setStyleSheet(
                "font-size: 25px; font-family: Arial; background-color: red; color: white;")
            
    def thruster_control(self):
        pass

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())