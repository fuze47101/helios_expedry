"""
ColormapEnum.py — Colormap Options for Thermal Display
ExpeDRY FeatherV2

Maps colormap names to OpenCV colormap constants.
"""

import cv2
from enum import IntEnum


class Colormap(IntEnum):
    AUTUMN = cv2.COLORMAP_AUTUMN
    BONE = cv2.COLORMAP_BONE
    JET = cv2.COLORMAP_JET
    WINTER = cv2.COLORMAP_WINTER
    RAINBOW = cv2.COLORMAP_RAINBOW
    OCEAN = cv2.COLORMAP_OCEAN
    SUMMER = cv2.COLORMAP_SUMMER
    SPRING = cv2.COLORMAP_SPRING
    COOL = cv2.COLORMAP_COOL
    HOT = cv2.COLORMAP_HOT
    INFERNO = cv2.COLORMAP_INFERNO
    MAGMA = cv2.COLORMAP_MAGMA
    TURBO = cv2.COLORMAP_TURBO


# Default colormap for thermal display
DEFAULT = Colormap.JET
