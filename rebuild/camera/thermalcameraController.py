"""
thermalcameraController.py — IR Thermal Camera Data Processing
ExpeDRY FeatherV2

Processes raw thermal data from the IR camera (256×192).
The camera outputs a combined frame: top half is visible image,
bottom half is thermal data. This module handles the thermal half.

Usage:
    tc = ThermalCameraController()
    raw_temp = tc.calculateRawTemperature(thdata)
    temp = tc.calculateTemperature(thdata)
    min_t = tc.calculateMinimumTemperature(thdata)
    max_t = tc.calculateMaximumTemperature(thdata)
    avg_t = tc.calculateAverageTemperature(thdata)
"""

import numpy as np
from camera.values import TEMP_SCALE, TEMP_OFFSET


class ThermalCameraController:

    def __init__(self):
        self._raw_temp = None
        self._temp_matrix = None

    def calculateRawTemperature(self, thdata):
        """Extract raw temperature matrix from thermal data frame.

        Args:
            thdata: numpy array — bottom half of camera frame (thermal data)

        Returns:
            2D numpy array of raw temperature values
        """
        if thdata is None or thdata.size == 0:
            return np.zeros((192, 256), dtype=np.float32)

        try:
            # Thermal data is encoded in the pixel values
            # Convert BGR to single-channel thermal data
            # The camera packs 16-bit temps into the blue and green channels
            if len(thdata.shape) == 3:
                # Combine low byte (blue) + high byte (green) into 16-bit values
                raw = thdata[:, :, 0].astype(np.uint16) | (thdata[:, :, 1].astype(np.uint16) << 8)
            else:
                raw = thdata.astype(np.uint16)

            self._raw_temp = raw.astype(np.float32)
            return self._raw_temp
        except Exception as e:
            print(f"Raw temp calculation error: {e}")
            return np.zeros((192, 256), dtype=np.float32)

    def calculateTemperature(self, thdata):
        """Convert raw thermal data to temperature matrix in Celsius.

        Args:
            thdata: numpy array — thermal data frame

        Returns:
            2D numpy array of temperatures in °C
        """
        if self._raw_temp is None:
            self.calculateRawTemperature(thdata)

        try:
            self._temp_matrix = self._raw_temp / TEMP_SCALE - TEMP_OFFSET
            return self._temp_matrix
        except Exception:
            return np.zeros((192, 256), dtype=np.float32)

    def calculateMinimumTemperature(self, thdata):
        """Get minimum temperature in the frame.

        Returns:
            float — minimum temperature in °C
        """
        if self._temp_matrix is None:
            self.calculateTemperature(thdata)
        try:
            return float(np.min(self._temp_matrix))
        except:
            return 0.0

    def calculateMaximumTemperature(self, thdata):
        """Get maximum temperature in the frame.

        Returns:
            float — maximum temperature in °C
        """
        if self._temp_matrix is None:
            self.calculateTemperature(thdata)
        try:
            return float(np.max(self._temp_matrix))
        except:
            return 0.0

    def calculateAverageTemperature(self, thdata):
        """Get average temperature in the frame.

        Returns:
            float — average temperature in °C
        """
        if self._temp_matrix is None:
            self.calculateTemperature(thdata)
        try:
            return float(np.mean(self._temp_matrix))
        except:
            return 0.0
