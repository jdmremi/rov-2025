from PyQt5.QtWidgets import QWidget, QLabel
from PyQt5.QtCore import pyqtSlot
import numpy as np
import logging
import coloredlogs

# Local
from videothread import VideoThread

WINDOW_TITLE = "ROV Control"
VIDEO_WIDTH = int(640*1.25)
VIDEO_HEIGHT = int(480)
WINDOW_WIDTH = 1920
WINDOW_HEIGHT = 1080
GREEN_TEXT_CSS = "color: green"
RED_TEXT_CSS = "color: red"

coloredlogs.install(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class VideoWidget(QWidget):
    """
    VideoWidget is a PyQt5-based widget that displays video feed from a camera using a QLabel.
    It initializes a video capture thread to process and display frames in real-time.

    Attributes:
        __image_label (QLabel): A QLabel widget used to display the video frames.
        __video_thread (VideoThread): A thread responsible for capturing and processing video frames.

    Methods:
        __init__(width, height):
            Initializes the VideoWidget with a specified width and height for the video display.
        update_image(cv_img):
            Updates the QLabel with a new image frame received from the video thread.
        get_video_thread():
            Returns the video capture thread instance.
    """

    def __init__(self, width, height, camera_index):
        """
        Initializes the VideoWidget instance.

        Args:
            width (int): The width of the video display area.
            height (int): The height of the video display area.

        Attributes:
            __image_label (QLabel): A QLabel widget used to display the video frames.
            __video_thread (VideoThread): A thread responsible for capturing video frames
                and emitting a signal to update the display.
        """
        super().__init__()
        logger.info("Video thread initialized")
        
        
        logger.info(f"[VideoWidget] Opening camera index: {camera_index}")



        # Part of the GUI which displays the camera input.
        self.__image_label = QLabel(self)
        self.__image_label.setFixedSize(int(width), int(height))
        self.__image_label.setScaledContents(True)
        # create the video capture thread, attach the event handler, and start it.
        self.__video_thread = VideoThread(width, height, camera_index)
        self.__video_thread.change_pixmap_signal.connect(self.update_image)
        self.__video_thread.start()

    # Event handler for updating the image_label with a new opencv image.
    @pyqtSlot(np.ndarray)
    def update_image(self, cv_img):
        """
        Slot to update the displayed image in the video widget.

        This method is triggered when a new frame (as a NumPy array) is emitted.
        It converts the OpenCV image to a QPixmap using the `convert_cv_qt` method
        from the video thread and updates the image label with the new pixmap.

        Args:
            cv_img (np.ndarray): The new frame to be displayed, represented as a NumPy array.
        """
        qt_img = self.__video_thread.convert_cv_qt(cv_img)
        self.__image_label.setPixmap(qt_img)

    def get_video_thread(self):
        """
        Retrieves the video thread instance.

        Returns:
            Thread: The video thread instance associated with this object.
        """
        return self.__video_thread
