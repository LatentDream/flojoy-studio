import serial.tools.list_ports
import pyvisa
import cv2
import subprocess
from sys import platform
from abc import ABC, abstractmethod

from captain.types.devices import CameraDevice, SerialDevice, VISADevice

__all__ = ["get_device_finder"]


class DeviceFinder(ABC):
    @abstractmethod
    def get_cameras(self) -> list[CameraDevice]:
        """Returns a list of camera indices connected to the system."""
        pass

    def get_serial_devices(self) -> list[SerialDevice]:
        """Returns a list of serial devices connected to the system."""
        ports = serial.tools.list_ports.comports()

        return [
            SerialDevice(port=p.device, description=p.description, hwid=p.hwid)
            for p in ports
        ]

    def get_visa_devices(self) -> list[VISADevice]:
        """Returns a list of VISA devices connected to the system."""
        rm = pyvisa.ResourceManager("@py")
        return [
            VISADevice(name=addr.split("::")[0], address=addr)
            for addr in rm.list_resources()
        ]


class LinuxDeviceFinder(DeviceFinder):
    def get_cameras(self) -> list[CameraDevice]:
        command = r"v4l2-ctl --list-devices | grep -A1 -P '^[^\s-][^:]+'"
        result = subprocess.run(command, shell=True, text=True, stdout=subprocess.PIPE)

        # filter out empty lines
        lines = list(filter(None, result.stdout.split("\n")))

        # output is formatted in groups of 2 lines
        # {camera name}
        # {port}
        cameras = [
            CameraDevice(name=lines[i].strip(), id=lines[i + 1].strip())
            for i in range(len(lines) // 2)
        ]

        return cameras

        # i = 0
        # cameras = []
        #
        # while True:
        #     camera = cv2.VideoCapture(i)
        #     if not camera.read()[0]:
        #         break
        #     else:
        #         cameras.append(i)
        #     camera.release()
        #     i += 1
        #
        # return cameras


class MacOSDeviceFinder(DeviceFinder):
    def get_cameras(self):
        # command = r"v4l2-ctl --list-devices | grep -oP '^[^\s-][^:]+'"
        # result = subprocess.run(command, shell=True, text=True, stdout=subprocess.PIPE)
        # cameras = result.stdout.split("\n")
        #
        # # filter out empty strings
        # return [c for c in cameras if c]
        i = 0
        cameras = []

        while True:
            camera = cv2.VideoCapture(i)
            if not camera.read()[0]:
                break
            else:
                cameras.append(i)
            camera.release()
            i += 1

        return [CameraDevice(name=f"Camera {i}", id=i) for i in cameras]


class WindowsDeviceFinder(DeviceFinder):
    def __init__(self):
        raise NotImplementedError()

    def get_cameras(self):
        raise NotImplementedError()


def get_device_finder():
    if platform == "win32":
        return WindowsDeviceFinder()
    elif platform == "darwin":
        return MacOSDeviceFinder()

    return LinuxDeviceFinder()