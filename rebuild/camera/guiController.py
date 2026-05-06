"""
guiController.py — Thermal Heatmap Rendering with OpenCV
ExpeDRY FeatherV2

Renders the thermal camera data as a colorized heatmap with
temperature overlays (min, max, avg).

Usage:
    gc = GuiController(width=256, height=192)
    heatmap = gc.drawGUI(imdata, temp, maxTemp, minTemp, averageTemp, ...)
"""

import cv2
import numpy as np
from camera.ColormapEnum import DEFAULT as DEFAULT_COLORMAP


class GuiController:

    def __init__(self, width=256, height=192):
        self.width = width
        self.height = height
        self.colormap = DEFAULT_COLORMAP

    def drawGUI(self, imdata, temp, maxTemp, minTemp, averageTemp,
                isRecording=False, mcol=0, mrow=0, lcol=0, lrow=0):
        """Render thermal heatmap with overlays.

        Args:
            imdata: numpy array — visible image data (top half of camera frame)
            temp: numpy array — temperature matrix (°C)
            maxTemp: float — maximum temperature in frame
            minTemp: float — minimum temperature in frame
            averageTemp: float — average temperature in frame
            isRecording: bool — show recording indicator
            mcol, mrow: int — max temp cursor position
            lcol, lrow: int — min temp cursor position

        Returns:
            numpy array — BGR image ready for display
        """
        try:
            # Normalize temperature matrix to 0-255 for colormap
            if temp is not None and temp.size > 0:
                t_min = np.min(temp)
                t_max = np.max(temp)
                t_range = t_max - t_min if t_max > t_min else 1.0

                normalized = ((temp - t_min) / t_range * 255).astype(np.uint8)
                heatmap = cv2.applyColorMap(normalized, int(self.colormap))
            else:
                # Fallback: just use the visible image
                heatmap = imdata.copy() if imdata is not None else np.zeros(
                    (self.height, self.width, 3), dtype=np.uint8)

            # Resize to match expected output dimensions
            heatmap = cv2.resize(heatmap, (self.width, self.height))

            # Draw temperature text overlays
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.45
            thickness = 1

            # Max temp (red)
            max_text = f"Max: {maxTemp:.1f}C"
            cv2.putText(heatmap, max_text, (5, 15),
                       font, font_scale, (0, 0, 255), thickness)

            # Min temp (blue)
            min_text = f"Min: {minTemp:.1f}C"
            cv2.putText(heatmap, min_text, (5, 35),
                       font, font_scale, (255, 100, 0), thickness)

            # Avg temp (white)
            avg_text = f"Avg: {averageTemp:.1f}C"
            cv2.putText(heatmap, avg_text, (5, 55),
                       font, font_scale, (255, 255, 255), thickness)

            # Recording indicator
            if isRecording:
                cv2.circle(heatmap, (self.width - 15, 15), 8, (0, 0, 255), -1)

            return heatmap

        except Exception as e:
            print(f"GUI render error: {e}")
            return np.zeros((self.height, self.width, 3), dtype=np.uint8)
