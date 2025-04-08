import logging
import os
from os.path import join, abspath
from typing import LiteralString

from PySide6.QtWidgets import QApplication, QMessageBox
import sys
sys.setrecursionlimit(1500)
from image_set_reader import ImageSetBlobDetector
from blob_detector_ui import BlobDetectorUI
from blob_detector_logic import BlobDetectorLogic
from utils import DEFAULT_IMAGE_PATH

if __name__ == "__main__":
    app = QApplication([])

    def resource_path(relative_path) -> LiteralString | str | bytes:
        if hasattr(sys, '_MEIPASS'):
            return join(sys._MEIPASS, relative_path)
        return join(abspath("."), relative_path)

    # Load and apply the stylesheet
    with open(resource_path("style.qss"), "r") as file:
        app.setStyleSheet(file.read())

    # Handle command line arguments for mode
    if len(sys.argv) != 2:
        mode = "image_set"
        logging.warning("No mode specified. Defaulting to image_set mode.")
    else:
        mode = sys.argv[1]

    # Load the program into the correct mode
    if mode == "single_image":
        blob_detector_logic = BlobDetectorLogic(DEFAULT_IMAGE_PATH)
        logging.debug("Single image mode")
        logging.debug("Image path: %s", blob_detector_logic.image_path)
        widget = BlobDetectorUI(blob_detector_logic)
        widget.update_display_image()  # Ensure the image is displayed
    elif mode == "image_set":
        widget = ImageSetBlobDetector()

    widget.show()
    app.exec()