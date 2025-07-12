import logging

from PySide6.QtWidgets import QApplication, QMessageBox
import sys
sys.setrecursionlimit(1500)
from image_set_reader import ImageSetBlobDetector
from blob_detector_ui import BlobDetectorUI
from blob_detector_logic import BlobDetectorLogic
from utils import DEFAULT_IMAGE_PATH

if __name__ == "__main__":
    app = QApplication([])

    # Load and apply the stylesheet
    with open("style.qss", "r") as file:
        app.setStyleSheet(file.read())

    if len(sys.argv) != 2:
        QMessageBox.critical(None, "Error", "Usage: main.py <mode>\nModes: image_set, single_blob")
        sys.exit(1)

    mode = sys.argv[1]

    if mode == "image_set":
        widget = ImageSetBlobDetector()
    elif mode == "single_image":
        blob_detector_logic = BlobDetectorLogic(DEFAULT_IMAGE_PATH)
        logging.debug("Single image mode")
        logging.debug("Image path: %s", blob_detector_logic.image_path)
        widget = BlobDetectorUI(blob_detector_logic)
        widget.update_display_image()  # Ensure the image is displayed
    else:
        QMessageBox.critical(None, "Error", f"Unknown mode: {mode}\nModes: image_set, single_blob")
        sys.exit(1)

    widget.show()
    app.exec()