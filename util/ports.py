# Alphabetically lists the ports by name
import serial.tools.list_ports as ports


def comslist():
    com_ports = list(ports.comports())  # create a list of com ['COM1','COM2']
    for i in com_ports:
        print(i.device)  # returns 'COMx'


if __name__ == "__main__":
    comslist()
