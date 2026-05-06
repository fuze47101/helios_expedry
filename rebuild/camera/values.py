"""
values.py — Camera Constants
ExpeDRY FeatherV2

Constants for the 256×192 IR thermal camera (InfiRay/TopDon style).
"""

# Camera resolution
CAMERA_WIDTH = 256
CAMERA_HEIGHT = 192

# Temperature calculation constants (typical InfiRay sensor)
# Raw pixel value → temperature conversion
# T = raw / scale - offset
TEMP_SCALE = 64.0
TEMP_OFFSET = 273.15  # Kelvin to Celsius

# Display range defaults
TEMP_MIN_DEFAULT = 15.0   # °C
TEMP_MAX_DEFAULT = 45.0   # °C

# Colormap default
DEFAULT_COLORMAP = 2  # COLORMAP_JET in OpenCV
