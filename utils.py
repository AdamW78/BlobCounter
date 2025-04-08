from collections import namedtuple

# Constants
DEFAULT_DISPLAY_SCALE_FACTOR = 0.5
MIN_DISTANCE_BETWEEN_BLOBS = 1
MAX_DISTANCE_BETWEEN_BLOBS = 100
MIN_THRESHOLD = 1
MAX_THRESHOLD = 255
MIN_AREA = 1
MAX_AREA = 8000

DEFAULT_MIN_DISTANCE_BETWEEN_BLOBS = 1
DEFAULT_BLOB_COLOR = 1
DEFAULT_IMAGE_PATH = r'images/Arginine CLS with pH/Day 19/19_23_2nd_dilution.JPG'
CIRCLE_COLOR = (0, 0, 255)
CIRCLE_THICKNESS = 10
MIN_SCALE_FACTOR = 0.1
MAX_SCALE_FACTOR = 5.0
NEW_KEYPOINT_SIZE = 40
GRAPHICS_VIEW_HEIGHT = 600
GRAPHICS_VIEW_WIDTH = 800
DEFAULT_DILUTION = "3rd"
USE_DILUTION = True
USE_DAY = True
IMAGE_LIST_WIDGET_WIDTH = 300

# Slider names
SLIDER_NAME_MIN_AREA = 'Min Area'
SLIDER_NAME_MAX_AREA = 'Max Area'
SLIDER_NAME_MIN_CIRCULARITY = 'Min Circularity'
SLIDER_NAME_MIN_CONVEXITY = 'Min Convexity'
SLIDER_NAME_MIN_INERTIA_RATIO = 'Min Inertia Ratio'
SLIDER_NAME_MIN_DIST_BETWEEN_BLOBS = 'Min Dist Between Blobs'
SLIDER_NAME_MIN_THRESHOLD = 'Min Threshold'
SLIDER_NAME_MAX_THRESHOLD = 'Max Threshold'

# Slider values
SLIDER_MIN_VALUE = 0
SLIDER_MAX_VALUE = 100
SLIDER_MAX_THRESHOLD_VALUE = 255

# Default values
DEFAULT_MIN_AREA = 144
DEFAULT_MAX_AREA = 5000
DEFAULT_MIN_CIRCULARITY = 0.4  # Represented as 0.4 * 100
DEFAULT_MIN_CONVEXITY = 0.8    # Represented as 0.8 * 100
DEFAULT_MIN_INERTIA_RATIO = 0.01 # Represented as 0.01 * 100
DEFAULT_MIN_DIST_BETWEEN_BLOBS = 10
DEFAULT_MIN_THRESHOLD = 100
DEFAULT_MAX_THRESHOLD = 160
DEFAULT_MAX_UNDO_REDO_STACK_SIZE = 50
DEFAULT_KEYPOINT_SIZE_ADJUSTMENT_STEP = 1 # Step size for increasing/decreasing manually added keypoint size

# Tooltips
TOOLTIP_MIN_AREA = "Set the minimum area (in pixels) for a region to be considered a blob."
TOOLTIP_MAX_AREA = "Set the maximum area (in pixels) for a region to be considered a blob."
TOOLTIP_MIN_CIRCULARITY = "Set the minimum circularity (0-1) for a region to be considered a blob. Higher values mean more circular blobs."
TOOLTIP_MIN_CONVEXITY = "Set the minimum convexity (0-1) for a region to be considered a blob. Higher values mean more convex blobs."
TOOLTIP_MIN_INERTIA_RATIO = "Set the minimum inertia ratio (0-1) for a region to be considered a blob. Higher values mean more elongated blobs."
TOOLTIP_MIN_DIST_BETWEEN_BLOBS = "Set the minimum distance (in pixels) between blobs to be considered separate."
TOOLTIP_MIN_THRESHOLD = "Set the minimum threshold value for blob detection. Lower values detect darker blobs."
TOOLTIP_MAX_THRESHOLD = "Set the maximum threshold value for blob detection. Higher values detect lighter blobs."

Timepoint = namedtuple("Timepoint", ["day", "sample_number", "dilution", "num_keypoints", "filename"])