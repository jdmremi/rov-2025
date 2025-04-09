import sys
import cv2
import numpy as np
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QToolBar, QAction, QFileDialog, QLabel, QWidget, QHBoxLayout

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Dual Camera Application")
        self.toolbar = QToolBar()
        self.addToolBar(self.toolbar)

        # Layout for two video labels
        self.video_widget = QWidget()
        self.layout = QHBoxLayout()
        self.label1 = QLabel()
        self.label2 = QLabel()
        self.label1.setAlignment(Qt.AlignCenter)
        self.label2.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.label1)
        self.layout.addWidget(self.label2)
        self.video_widget.setLayout(self.layout)
        self.setCentralWidget(self.video_widget)

        # Camera threads
        self.camera1 = CameraThread(0)
        self.camera2 = CameraThread(1)

        self.camera1.image.connect(self.update_image1)
        self.camera2.image.connect(self.update_image2)

        self.camera1.start()
        self.camera2.start()

        capture_action = QAction("Capture", self.toolbar)
        capture_action.setShortcut("Space")
        capture_action.triggered.connect(self.capture_photo)
        self.toolbar.addAction(capture_action)

    def update_image1(self, frame):
        self.display_frame(frame, self.label1)

    def update_image2(self, frame):
        self.display_frame(frame, self.label2)

    def display_frame(self, frame, label):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = QImage(rgb_frame, rgb_frame.shape[1], rgb_frame.shape[0], QImage.Format_RGB888)
        label.setPixmap(QPixmap.fromImage(image))

    def capture_photo(self):
        for idx, cam in enumerate([self.camera1, self.camera2], start=1):
            if cam.frame is not None:
                rgb = cv2.cvtColor(cam.frame, cv2.COLOR_BGR2RGB)
                image = QImage(rgb, rgb.shape[1], rgb.shape[0], QImage.Format_RGB888)
                filename, _ = QFileDialog.getSaveFileName(self, f"Save Photo from Camera {idx}", "", "JPEG Image (*.jpg)")
                if filename:
                    image.save(filename, "jpg")

class CameraThread(QThread):
    image = pyqtSignal(np.ndarray)

    def __init__(self, camera_index):
        super().__init__()
        self.capture = cv2.VideoCapture(camera_index)
        self.frame = None

    def run(self):
        while True:
            ret, frame = self.capture.read()
            if ret:
                self.frame = frame
                self.image.emit(frame)

    def stop(self):
        if self.capture:
            self.capture.release()
        self.quit()
        self.wait()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
