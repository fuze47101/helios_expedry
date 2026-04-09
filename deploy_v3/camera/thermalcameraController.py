"""
thermalcameraController.py — IR Thermal Camera Data Processing
InfiRay 256x192 thermal camera.
"""
import numpy as np
from camera.values import TEMP_SCALE, TEMP_OFFSET


class ThermalCameraController:
    def __init__(self):
        self._raw_temp = None
        self._temp_matrix = None
        self._valid_mask = None
        # Exclude border pixels (camera often encodes metadata there)
        self._border = 4

    def calculateRawTemperature(self, thdata):
        if thdata is None or thdata.size == 0:
            return np.zeros((192, 256), dtype=np.float32)
        try:
            if len(thdata.shape) == 3:
                raw = thdata[:, :, 0].astype(np.uint16) | (thdata[:, :, 1].astype(np.uint16) << 8)
            else:
                raw = thdata.astype(np.uint16)
            self._raw_temp = raw.astype(np.float32)
            return self._raw_temp
        except Exception:
            return np.zeros((192, 256), dtype=np.float32)

    def calculateTemperature(self, thdata):
        if self._raw_temp is None:
            self.calculateRawTemperature(thdata)
        try:
            self._temp_matrix = self._raw_temp / TEMP_SCALE - TEMP_OFFSET
            # Valid mask: exclude borders and outlier temps
            b = self._border
            h, w = self._temp_matrix.shape
            self._valid_mask = np.zeros_like(self._temp_matrix, dtype=bool)
            inner = self._temp_matrix[b:h-b, b:w-b]
            inner_mask = (inner > -10.0) & (inner < 80.0)
            self._valid_mask[b:h-b, b:w-b] = inner_mask
            return self._temp_matrix
        except Exception:
            return np.zeros((192, 256), dtype=np.float32)

    def calculateMinimumTemperature(self, thdata):
        if self._temp_matrix is None:
            self.calculateTemperature(thdata)
        try:
            valid = self._temp_matrix[self._valid_mask]
            if valid.size > 0:
                return float(np.percentile(valid, 2))
            return 0.0
        except:
            return 0.0

    def calculateMaximumTemperature(self, thdata):
        if self._temp_matrix is None:
            self.calculateTemperature(thdata)
        try:
            valid = self._temp_matrix[self._valid_mask]
            if valid.size > 0:
                return float(np.percentile(valid, 98))
            return 0.0
        except:
            return 0.0

    def calculateAverageTemperature(self, thdata):
        if self._temp_matrix is None:
            self.calculateTemperature(thdata)
        try:
            valid = self._temp_matrix[self._valid_mask]
            if valid.size > 0:
                return float(np.mean(valid))
            return 0.0
        except:
            return 0.0
