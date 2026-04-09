"""
guiController.py — Thermal Heatmap Rendering with OpenCV
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
        try:
            if temp is not None and temp.size > 0:
                # Normalize using the actual valid min/max (not outliers)
                t_min = max(minTemp, -10.0)
                t_max = min(maxTemp, 80.0)
                if t_max <= t_min:
                    t_max = t_min + 1.0

                # Clip temp matrix to valid range for colormap
                clipped = np.clip(temp, t_min, t_max)
                normalized = ((clipped - t_min) / (t_max - t_min) * 255).astype(np.uint8)
                heatmap = cv2.applyColorMap(normalized, int(self.colormap))
            else:
                heatmap = imdata.copy() if imdata is not None else np.zeros(
                    (self.height, self.width, 3), dtype=np.uint8)

            heatmap = cv2.resize(heatmap, (self.width, self.height))

            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.45
            thickness = 1

            max_text = f"Max: {maxTemp:.1f}C"
            cv2.putText(heatmap, max_text, (5, 15),
                       font, font_scale, (0, 0, 255), thickness)

            min_text = f"Min: {minTemp:.1f}C"
            cv2.putText(heatmap, min_text, (5, 35),
                       font, font_scale, (255, 100, 0), thickness)

            avg_text = f"Avg: {averageTemp:.1f}C"
            cv2.putText(heatmap, avg_text, (5, 55),
                       font, font_scale, (255, 255, 255), thickness)

            if isRecording:
                cv2.circle(heatmap, (self.width - 15, 15), 8, (0, 0, 255), -1)

            return heatmap

        except Exception as e:
            return np.zeros((self.height, self.width, 3), dtype=np.uint8)
