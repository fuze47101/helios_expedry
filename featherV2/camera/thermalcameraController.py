import cv2, time, os
import numpy as np

from camera.values import *

from camera.ColormapEnum import Colormap
from camera.guiController import GuiController

class ThermalCameraController:
    def __init__(self, 
                 deviceIndex: int = VIDEO_DEVICE_INDEX, 
                 width: int = SENSOR_WIDTH, 
                 height: int = SENSOR_HEIGHT, 
                 fps: int = DEVICE_FPS, 
                 deviceName: str = DEVICE_NAME, 
                 mediaOutputPath: str = MEDIA_OUTPUT_PATH):
        # Parameters init
        self._deviceIndex: int = deviceIndex
        self._deviceName: str = deviceName
        self._width: int = width
        self._height: int = height
        self._fps: int = fps

        # Calculated values init
        self._rawTemp = TEMPERATURE_RAW
        self._temp = TEMPERATURE
        self._maxTemp = TEMPERATURE_MAX
        self._minTemp = TEMPERATURE_MIN
        self._avgTemp = TEMPERATURE_AVG
        self._mcol: int = 0
        self._mrow: int = 0
        self._lcol: int = 0
        self._lrow: int = 0
        

    def normalizeTemperature(self, rawTemp: float, d: int = 64, c: float = 273.15) -> float:
        """
        Normalizes/converts the raw temperature data using the formula found by LeoDJ.
        Link: https://www.eevblog.com/forum/thermal-imaging/infiray-and-their-p2-pro-discussion/200/
        """
        return (rawTemp/d) - c

    def calculateTemperature(self, thdata):
        """
        Calculates the (normalized) temperature of the frame.
        """
        raw = self.calculateRawTemperature(thdata)
        return round(self.normalizeTemperature(raw), TEMPERATURE_SIG_DIGITS)

    def calculateRawTemperature(self, thdata):
        """
        Calculates the raw temperature of the frame.
        """
        hi = int(thdata[96][128][0])
        lo = int(thdata[96][128][1])
        lo = lo * 256
        return hi+lo

    def calculateAverageTemperature(self, thdata):
        """
        Calculates the average temperature of the frame.
        """
        loavg = int(thdata[...,1].mean())
        hiavg = int(thdata[...,0].mean())
        loavg = loavg * 256
        return round(self.normalizeTemperature(loavg+hiavg), TEMPERATURE_SIG_DIGITS)

    def calculateMinimumTemperature(self, thdata):
        """
        Calculates the minimum temperature of the frame.
        """
        # Find the min temperature in the frame
        lomin = int(thdata[...,1].min())
        posmin = int(thdata[...,1].argmin())
        
        # Since argmax returns a linear index, convert back to row and col
        self._lcol, self._lrow = divmod(posmin, self._width)
        himin = int(thdata[self._lcol][self._lrow][0])
        lomin = lomin * 256
        
        return round(self.normalizeTemperature(himin+lomin), TEMPERATURE_SIG_DIGITS)

    def calculateMaximumTemperature(self, thdata):
        """
        Calculates the maximum temperature of the frame.
        """
        # Find the max temperature in the frame
        lomax = int(thdata[...,1].max())
        posmax = int(thdata[...,1].argmax())

        # Since argmax returns a linear index, convert back to row and col
        self._mcol, self._mrow = divmod(posmax, self._width)
        himax = int(thdata[self._mcol][self._mrow][0])
        lomax = lomax * 256
        
        return round(self.normalizeTemperature(himax+lomax), TEMPERATURE_SIG_DIGITS)

    # def run(self):
    #     """
    #     Runs the main runtime loop for the program.
    #     """
    #     # Initialize video
    #     self._cap = cv2.VideoCapture(self._deviceIndex)

    #     """
    #     MAJOR CHANGE: Do NOT convert to RGB. For some reason, this breaks the frame temperature data on TS001.
    #     Originally, it was the opposite: https://stackoverflow.com/questions/63108721/opencv-setting-videocap-property-to-cap-prop-convert-rgb-generates-weird-boolean
    #     """
    #     #cap.set(cv2.CAP_PROP_CONVERT_RGB, 0)

    #     # Start main runtime loop
    #     while(self._cap.isOpened()):
    #         ret, frame = self._cap.read()
    #         if ret == True:
    #             # Split frame into two parts: image data and thermal data
    #             imdata, thdata = np.array_split(frame, 2)
                
    #             # Now parse the data from the bottom frame and convert to temp!
    #             # Grab data from the center pixel...
    #             self._rawTemp = self.calculateRawTemperature(thdata)
    #             self._temp = self.calculateTemperature(thdata)

    #             # Calculate minimum temperature
    #             self._minTemp = self.calculateMinimumTemperature(thdata)
                
    #             # Calculate maximum temperature
    #             self._maxTemp = self.calculateMaximumTemperature(thdata)

    #             # Find the average temperature in the frame
    #             self._avgTemp = self.calculateAverageTemperature(thdata)
                
    #             # Draw GUI elements
    #             heatmap = self._guiController.drawGUI(
    #                 imdata=imdata,
    #                 temp=self._temp,
    #                 maxTemp=self._maxTemp,
    #                 minTemp=self._minTemp,
    #                 averageTemp=self._avgTemp,
    #                 isRecording=self._isRecording,
    #                 mcol=self._mcol,
    #                 mrow=self._mrow,
    #                 lcol=self._lcol,
    #                 lrow=self._lrow)
