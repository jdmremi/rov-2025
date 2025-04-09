import cv2
import numpy as np
from PyQt5.QtCore import pyqtSignal, QThread
from PyQt5.QtGui import QPixmap
from PyQt5 import QtGui
from PyQt5.QtCore import Qt
import logging
import coloredlogs
import os
import random
import string

coloredlogs.install(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class VideoThread(QThread):
    """
    VideoThread is a QThread subclass designed to handle video capture and processing in a separate thread. 
    It emits a signal with the captured video frames and provides utility methods for converting frames 
    to QPixmap and saving screenshots.

    Attributes:
        change_pixmap_signal (pyqtSignal): Signal emitted with a numpy array representing the video frame.
        __run_flag (bool): Internal flag to control the thread's execution.
        __display_width (int): Width of the display for scaling the video frames.
        __display_height (int): Height of the display for scaling the video frames.
        __recent_frame (np.ndarray): Stores the most recent video frame captured.

    Methods:
        __init__(width, height):
            Initializes the VideoThread with the specified display width and height.

        run():
            Starts the video capture loop, emitting frames via the change_pixmap_signal.
            Captures video from the default webcam (device 0).

        stop():
            Stops the video capture loop and waits for the thread to finish.

        convert_cv_qt(cv_img):
            Converts an OpenCV image (numpy array) to a QPixmap for display in a PyQt application.

        save_screenshot(path="./rov_images/"):
            Saves the most recent video frame as a screenshot to the specified directory.
            Creates the directory if it does not exist.
    """
    change_pixmap_signal = pyqtSignal(np.ndarray)

    def __init__(self, width, height, camera_index = 0):
        """
        Initializes the VideoThread object with specified display dimensions.

        Args:
            width (int): The width of the display.
            height (int): The height of the display.
        """
        super().__init__()
        self.__camera_index = camera_index
        self.__run_flag = True
        self.__display_width = height
        self.__display_height = width
        self.__recent_frame = None

    def run(self):
        """
        Executes the video capture thread.

        This method captures video frames from the default webcam (device 0) and emits
        the frames using the `change_pixmap_signal` signal for further processing or display.
        It continuously reads frames while the `__run_flag` is set to True. If the camera
        input cannot be read, an error is logged. The video capture system is properly
        released when the thread stops.

        Raises:
            RuntimeError: If no camera is connected or the camera input cannot be read.

        Emits:
            change_pixmap_signal: A signal that emits the captured video frame (`cv_img`).

        Notes:
            - Ensure that a camera is connected to the system before running this method.
            - OpenCV does not provide a direct way to check the number of connected cameras.
        """
        # Capture from webcam 0. Device 0 is generally the only camera plugged in, but this will error if there are no cameras plugged in.
        # Sadly, OpenCV doesn't provide a straightforward way to get the number of cameras present.

        logger.info(f"[VideoThread] Opening camera index: {self.__camera_index}")
        cap = cv2.VideoCapture(self.__camera_index)
        while self.__run_flag:
            ret, cv_img = cap.read()
            if ret:
                self.change_pixmap_signal.emit(cv_img)
                self.__recent_frame = cv_img
            else:
                logger.error(
                    "Error reading camera input. Verify that the camera is connected and restart the application.")
        # shut down capture system
        cap.release()

    # Sets run flag to False and waits for thread to finish
    def stop(self):
        """
        Stops the video thread by setting the internal run flag to False and waits 
        for the thread to finish execution.

        This method ensures that the thread is properly terminated before proceeding.
        """
        self.__run_flag = False
        self.wait()

    def convert_cv_qt(self, cv_img):
        """
        Converts an OpenCV image to a QPixmap for display in a PyQt application.

        This method takes an image in OpenCV format (BGR) and converts it to a 
        QPixmap object, which can be used for rendering in PyQt widgets. The 
        conversion includes changing the color format from BGR to RGB, resizing 
        the image to fit the specified display dimensions, and maintaining the 
        aspect ratio.

        Args:
            cv_img (numpy.ndarray): The input image in OpenCV format (BGR).

        Returns:
            QPixmap: The converted image as a QPixmap object, ready for display.
        """
        """Convert from an opencv image to QPixmap"""
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QtGui.QImage(
            rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(
            self.__display_width, self.__display_height, Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)

    def save_screenshot(self, path="./rov_images/"):
        """
        Saves a screenshot of the most recent frame to the specified directory.

        Args:
            path (str): The directory where the screenshot will be saved. 
                        Defaults to "./rov_images/".

        Behavior:
            - If the specified directory does not exist, it will be created.
            - A random file name consisting of 6 uppercase letters and digits 
              will be generated for the screenshot.
            - The screenshot will be saved as a JPEG file in the specified directory.
            - Logs the full path of the saved screenshot.

        Note:
            - The method does nothing if there is no recent frame available.
        """
        if not os.path.exists(path):
            os.mkdir(path)

        # Generate random file name
        if self.__recent_frame is not None:
            file_name = ''.join(random.SystemRandom().choice(
                string.ascii_uppercase + string.digits) for _ in range(6))

            full_path = path + file_name + ".jpg"
            cv2.imwrite(full_path, self.__recent_frame)
            logger.info(f"Screenshot saved: {full_path}")
