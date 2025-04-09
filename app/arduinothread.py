import serial
from PyQt5.QtCore import pyqtSignal, QThread, QObject, QTimer, pyqtSlot
import platform
import serial.tools.list_ports as ports
import coloredlogs
import logging
import json
from queue import Queue
import time

coloredlogs.install(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class ArduinoReadWorker(QObject):
    """
    A worker class for reading data from an Arduino device via a serial port.

    This class runs a loop to continuously read data from the specified serial port,
    decode it, and emit a signal with the parsed data. It is designed to be used
    with PyQt's signal-slot mechanism for inter-thread communication.

    Attributes:
        arduino_data_channel_signal (pyqtSignal): A signal that emits a dictionary
            containing the parsed data received from the Arduino.
        serial_port (Serial): The serial port object used for communication with the Arduino.
        running (bool): A flag to control the reading loop. Set to `True` to keep
            reading data, and `False` to stop the loop.

    Methods:
        read_arduino():
            Continuously reads data from the serial port, decodes it, parses it as JSON,
            and emits the parsed data via the `arduino_data_channel_signal`. Handles
            exceptions that may occur during the reading or parsing process.
    """
    arduino_data_channel_signal = pyqtSignal(dict)

    def __init__(self, serial_port):
        """
        Initializes the ArduinoThread instance.

        Args:
            serial_port (str): The serial port used for communication with the Arduino.
        """
        super().__init__()
        self.serial_port = serial_port  # Serial port for communication with Arduino
        self.running = True  # Flag to control the reading loop

    def read_arduino(self):
        """
        Continuously reads data from the Arduino via the serial port while the thread is running.

        This method runs in a loop as long as the `self.running` flag is set to True. It reads 
        lines of data from the serial port, decodes them, and attempts to parse them as JSON. 
        If successful, it emits the parsed data through the `arduino_data_channel_signal`.

        If an error occurs during reading, decoding, or parsing, it logs a critical error message.

        Raises:
            Exception: Logs any exception that occurs during the reading or processing of data.

        Notes:
            - The serial port must be properly configured and opened before calling this method.
            - The `self.arduino_data_channel_signal` must be connected to a slot to handle the emitted data.
        """
        while self.running:
            try:
                # Read a line from the serial port and decode it
                payload = self.serial_port.readline().decode("utf-8")
                logger.debug(f"PAYLOAD = {payload}")
                if payload:
                    # Parse the JSON data
                    data = json.loads(payload)
                    # Emit the signal with the received data
                    self.arduino_data_channel_signal.emit(data)
            except Exception as e:
                logger.critical(f"Error reading Arduino: {e}")


class ArduinoWriteWorker(QObject):
    """
    A worker class for handling data communication with an Arduino device via a serial port.

    This class is designed to run in a separate thread and continuously send data
    from a queue to the Arduino in JSON format. It ensures that the communication
    is handled asynchronously and efficiently.

    Attributes:
        serial_port (serial.Serial): The serial port object used for communication with the Arduino.
        queue (queue.Queue): A thread-safe queue containing data to be sent to the Arduino.
        running (bool): A flag to control the execution of the writing loop.

    Methods:
        handle_data():
            Continuously checks the queue for data, converts it to JSON format, and sends it
            to the Arduino via the serial port. Handles exceptions during the write process
            and includes a small delay to prevent busy waiting.
    """

    def __init__(self, serial_port, queue):
        """
        Initializes the ArduinoThread instance.

        Args:
            serial_port (str): The serial port used for communication with the Arduino.
            queue (Queue): A queue object for handling data to be sent to the Arduino.

        Attributes:
            serial_port (str): Stores the serial port for communication with the Arduino.
            queue (Queue): Stores the queue for managing data to be sent to the Arduino.
            running (bool): A flag to control the writing loop, initialized to True.
        """
        super().__init__()
        self.serial_port = serial_port  # Serial port for communication with Arduino
        self.queue = queue  # Queue for handling data to be sent to Arduino
        self.running = True  # Flag to control the writing loop

    def handle_data(self):
        """
        Continuously handles data from a queue and sends it to the Arduino via a serial port.

        This method runs in a loop while the `running` attribute is True. It checks if the queue
        contains data, retrieves it, converts it to JSON format, and sends it to the Arduino
        through the serial port. A small delay is added to prevent busy waiting.

        Raises:
            Exception: If an error occurs while writing to the Arduino.

        Attributes:
            queue (Queue): A thread-safe queue containing data to be sent to the Arduino.
            serial_port (Serial): The serial port object used to communicate with the Arduino.
            running (bool): A flag indicating whether the loop should continue running.
        """
        while self.running:
            if not self.queue.empty():
                data = self.queue.get()  # Get data from the queue
                try:
                    # Convert data to JSON format and send to Arduino
                    payload = json.dumps(data) + '\0'
                    # logger.debug(f"Sending payload to Arduino: {payload}")
                    self.serial_port.write(bytes(payload, 'utf-8'))
                    self.serial_port.flush()
                except Exception as e:
                    logger.critical(f"Error writing to Arduino: {e}")
            time.sleep(0.1)  # Small delay to avoid busy waiting


class ArduinoThread(QThread):
    """
    ArduinoThread is a PyQt-based thread class that manages communication with an Arduino device
    via serial communication. It handles both reading and writing operations using separate worker
    threads to ensure non-blocking behavior.

    Attributes:
        arduino_data_channel_signal (pyqtSignal): Signal to emit data read from the Arduino.

    Methods:
        __init__():
            Initializes the ArduinoThread, sets up serial communication, and starts the
            reading and writing worker threads.
        __initialize_serial():
            Detects and initializes the serial port for communication with the Arduino.
        __list_ports():
            Lists all available serial ports on the system.
        stop():
            Stops the reading and writing worker threads and cleans up resources.
        handle_data(data):
            Queues data to be sent to the Arduino.
        forward_arduino_data(data):
            Emits a signal to forward data read from the Arduino to the main application.
    """
    arduino_data_channel_signal = pyqtSignal(dict)

    def __init__(self):
        """
        Initializes the ArduinoThread class.

        This constructor sets up the necessary components for communication with an Arduino device.
        It initializes a serial connection, creates worker objects for reading and writing data,
        and assigns them to separate threads for concurrent operation.

        Attributes:
            write_queue (Queue): A queue for managing data to be written to the Arduino.
            __serial (serial.Serial or None): The serial connection to the Arduino device.
            read_worker (ArduinoReadWorker): Worker object responsible for reading data from the Arduino.
            read_thread (QThread): Thread for running the read_worker.
            write_worker (ArduinoWriteWorker): Worker object responsible for writing data to the Arduino.
            write_thread (QThread): Thread for running the write_worker.

        Methods:
            __initialize_serial(): Private method to initialize the serial connection.
            forward_arduino_data(data): Method connected to the signal for forwarding Arduino data.

        Notes:
            If the serial connection is successfully initialized, separate threads for reading
            and writing data are started, and the workers are moved to their respective threads.
        """
        super().__init__()
        self.write_queue = Queue()
        self.__serial = None
        self.__initialize_serial()

        if self.__serial:
            # Initialize reading worker and thread
            self.read_worker = ArduinoReadWorker(self.__serial)
            self.read_thread = QThread()
            self.read_worker.moveToThread(self.read_thread)
            self.read_worker.arduino_data_channel_signal.connect(
                self.forward_arduino_data)
            self.read_thread.started.connect(self.read_worker.read_arduino)
            self.read_thread.start()

            # Initialize writing worker and thread
            self.write_worker = ArduinoWriteWorker(
                self.__serial, self.write_queue)
            self.write_thread = QThread()
            self.write_worker.moveToThread(self.write_thread)
            self.write_thread.started.connect(self.write_worker.handle_data)
            self.write_thread.start()

        logger.info("Arduino thread ready!")

    def __initialize_serial(self):
        """
        Initializes the serial connection to the Arduino device.

        This method identifies the appropriate serial port based on the operating 
        system and establishes a connection to the Arduino. It filters available 
        ports to find the one matching the expected naming convention for the 
        current platform.

        - For macOS (Darwin): Ports starting with "/dev/cu.usb".
        - For Linux: Ports starting with "/dev/ttyACM".
        - For Windows: Ports starting with "COM".

        If no matching port is found, a critical log message is generated. If a 
        matching port is found, the first available port is used to initialize 
        the serial connection with a baud rate of 9600.

        Logging:
            - Logs available ports at the debug level.
            - Logs the selected port at the debug level.
            - Logs a critical error if no matching port is found.

        Raises:
            serial.SerialException: If the serial connection cannot be established.

        Dependencies:
            - Requires the `serial` module for serial communication.
            - Requires the `platform` module to determine the operating system.
            - Requires a logger instance for logging messages.
        """
        port_filter = None
        available_ports = self.__list_ports()

        logger.debug(f"Available ports: {available_ports}")

        # Set port filter based on operating system
        match platform.system():
            case "Darwin":
                port_filter = "/dev/cu.usb"
            case "Linux":
                port_filter = "/dev/ttyACM"
            case "Windows":
                port_filter = "COM"

        # Filter ports based on the port filter
        filtered_ports = list(
            filter(lambda name: port_filter in name, available_ports))

        if len(filtered_ports) == 0:
            logger.critical(
                "Arduino port not found! Ensure proper connection.")
        else:
            port = filtered_ports[0]  # Use the first available port
            logger.debug(f"Using port: {port}")
            # Initialize serial connection
            self.__serial = serial.Serial(
                port=port, baudrate=9600, write_timeout=0, dsrdtr=True)
            logger.debug(f"Serial initialized: {self.__serial}")

    # Function to list available serial ports
    def __list_ports(self):
        """
        Lists all available serial ports.

        This method retrieves a list of all available serial ports on the system
        and returns their device names.

        Returns:
            list: A list of strings, where each string represents the device name
                  of an available serial port.
        """
        return [port.device for port in list(ports.comports())]

    # Function to stop the workers and threads
    def stop(self):
        """
        Stops the execution of the Arduino thread and its associated workers.

        This method ensures that both the reading and writing worker loops are stopped,
        their respective threads are properly quit and waited for, and the main thread
        is also terminated cleanly.

        Steps performed:
        1. Stops the reading worker loop if it exists.
        2. Stops the writing worker loop if it exists.
        3. Quits and waits for the read thread to finish.
        4. Quits and waits for the write thread to finish.
        5. Sets the internal run flag to False.
        6. Waits for the main thread to finish execution.
        """
        if self.read_worker:
            self.read_worker.running = False  # Stop the reading worker loop
        if self.write_worker:
            self.write_worker.running = False  # Stop the writing worker loop
        self.read_thread.quit()  # Quit the read thread
        self.read_thread.wait()  # Wait for the read thread to finish
        self.write_thread.quit()  # Quit the write thread
        self.write_thread.wait()  # Wait for the write thread to finish
        self._run_flag = False
        self.wait()  # Wait for the thread to finish

    # Function to handle data to be sent to Arduino
    def handle_data(self, data):
        """
        Handles incoming data by adding it to the write queue for processing.

        Args:
            data (Any): The data to be queued for sending to the Arduino.

        Notes:
            - The method places the provided data into the `write_queue`.
            - If the queue size grows excessively large (e.g., > 1000 items), 
              additional handling may be required to manage the queue size.
        """
        # logger.debug(f"Queueing data to send to Arduino: {data}")
        self.write_queue.put(data)  # Put data in the queue

        # If queue becomes too big (> 1000), we might need to clear it.
        # logger.debug(f"Queue size: {self.write_queue.qsize()}")

    # Slot to forward data read from Arduino to the main application
    @pyqtSlot(dict)
    def forward_arduino_data(self, data):
        """
        Forwards data received from the Arduino to the main thread via a PyQt signal.

        This method is a PyQt slot that emits the `arduino_data_channel_signal` signal
        with the provided data dictionary. It is typically used to transfer data
        between threads in a PyQt application.

        Args:
            data (dict): The data received from the Arduino to be forwarded.
        """
        # logger.debug(f"Forwarding data to main thread: {data}")
        self.arduino_data_channel_signal.emit(data)
