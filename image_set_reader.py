import logging
from time import sleep, time

from PySide6.QtGui import QWheelEvent

from blob_counter_worker import BlobCounterWorker
from ui_utils import UIUtils

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
import math
import os
import xml.dom.minidom
import xml.etree.ElementTree as ET
import cv2
from PySide6.QtCore import Qt, QEvent, QThread
from PySide6.QtWidgets import QListWidget, QFileDialog, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, \
    QApplication, QGroupBox, QStackedWidget, QCheckBox, QProgressDialog, QMessageBox

from blob_detector_ui import BlobDetectorUI
from excel_output import ExcelOutput
from logger import LOGGER
from utils import DEFAULT_DILUTION, IMAGE_LIST_WIDGET_WIDTH

class ImageSetBlobDetector(QWidget):
    def __init__(self):
        super().__init__()
        self.currently_updating = False
        self.blob_detector_logic_list= []
        self.image_paths = []
        self.timepoints = []
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Image Set Blob Detector")
        self.layout = QHBoxLayout(self)

        # Add image list widget
        self.create_image_list_widget()

        # Add blob detector UI
        self.blob_detector_stack = QStackedWidget()
        self.layout.addWidget(self.blob_detector_stack)
        self.progress_dialog = None

        # Add universal blob detector settings
        self.create_universal_blob_detector_settings()

        # Add a blank BlobDetectorUI widget initially
        blank_blob_detector = BlobDetectorUI(image_path=None, image_set_reader=self)
        self.blob_detector_stack.addWidget(blank_blob_detector)

        # Install event filters for zooming
        self.installEventFilter(self)

    # noinspection PyTypeChecker
    def eventFilter(self, source, event):
        if event.type() == QEvent.Type.MouseMove or event.type() == QEvent.Type.MouseButtonPress or event.type() == QEvent.Type.MouseButtonRelease:
            current_widget = self.blob_detector_stack.currentWidget()
            if isinstance(current_widget, BlobDetectorUI):
                return current_widget.handle_mouse_event(event)
        elif event.type() == QEvent.Type.Wheel:
            event = event if isinstance(event, QWheelEvent) else None
            current_widget = self.blob_detector_stack.currentWidget()
            if isinstance(current_widget, BlobDetectorUI):
                current_widget.handle_wheel_zoom(event)
                return True
        elif event.type() == QEvent.Type.KeyPress:
            current_widget = self.blob_detector_stack.currentWidget()
            if isinstance(current_widget, BlobDetectorUI):
                current_widget.handle_key_zoom(event)
                return True
        return super().eventFilter(source, event)

    def create_universal_blob_detector_settings(self):
        self.controls_group_box = QGroupBox("Blob Detection Parameters - All Images")
        self.controls_layout = QVBoxLayout()
        self.controls_group_box.setLayout(self.controls_layout)

        sliders = UIUtils.create_blob_detector_sliders()
        self.min_area_group_box, self.min_area_slider, self.min_area_input = sliders['min_area']
        self.max_area_group_box, self.max_area_slider, self.max_area_input = sliders['max_area']
        self.min_circularity_group_box, self.min_circularity_slider, self.min_circularity_input = sliders[
            'min_circularity']
        self.min_convexity_group_box, self.min_convexity_slider, self.min_convexity_input = sliders['min_convexity']
        self.min_inertia_ratio_group_box, self.min_inertia_ratio_slider, self.min_inertia_ratio_input = sliders[
            'min_inertia_ratio']
        self.min_dist_between_blobs_group_box, self.min_dist_between_blobs_slider, self.min_dist_between_blobs_input = \
        sliders['min_dist_between_blobs']
        self.min_threshold_group_box, self.min_threshold_slider, self.min_threshold_input = sliders['min_threshold']
        self.max_threshold_group_box, self.max_threshold_slider, self.max_threshold_input = sliders['max_threshold']

        self.controls_layout.addWidget(self.min_area_group_box)
        self.controls_layout.addWidget(self.max_area_group_box)
        self.controls_layout.addWidget(self.min_circularity_group_box)
        self.controls_layout.addWidget(self.min_convexity_group_box)
        self.controls_layout.addWidget(self.min_inertia_ratio_group_box)
        self.controls_layout.addWidget(self.min_dist_between_blobs_group_box)
        self.controls_layout.addWidget(self.min_threshold_group_box)
        self.controls_layout.addWidget(self.max_threshold_group_box)

        self.gaussian_blur_checkbox = QCheckBox('Apply Gaussian Blur')
        self.morphological_operations_checkbox = QCheckBox('Apply Morphological Operations')
        self.controls_layout.addWidget(self.gaussian_blur_checkbox)
        self.controls_layout.addWidget(self.morphological_operations_checkbox)

        self.open_folder_button = QPushButton('Open Image Set Folder...')
        # self.open_folder_button.setIcon(QIcon('icons/open.svg'))
        self.open_folder_button.clicked.connect(self.open_folder)
        self.controls_layout.addWidget(self.open_folder_button)

        self.update_all_button = QPushButton('Update Blob Count for All Images')
        # self.update_all_button.setIcon(QIcon('icons/update.svg'))
        self.update_all_button.clicked.connect(self.count_all_blobs)
        self.controls_layout.addWidget(self.update_all_button)
        self.update_all_button.setEnabled(False)

        self.export_button = QPushButton('Export Counted Images to XML and PNG')
        # self.export_button.setIcon(QIcon('icons/export.svg'))
        self.export_button.clicked.connect(self.export_counted_images)
        self.export_to_excel_button = QPushButton('Export Blob Counts to Excel')
        self.export_to_excel_button.clicked.connect(self.export_to_excel)


        self.controls_layout.addWidget(self.export_button)
        self.controls_layout.addWidget(self.export_to_excel_button)
        self.export_button.setEnabled(False)
        self.export_to_excel_button.setEnabled(False)
        self.layout.addWidget(self.controls_group_box)

    def create_image_list_widget(self):
        self.image_list_group_box = QGroupBox("Image List")
        self.image_list_layout = QVBoxLayout()
        self.image_list_widget = QListWidget()
        self.image_list_widget.setMinimumWidth(IMAGE_LIST_WIDGET_WIDTH)
        self.image_list_widget.setMaximumWidth(IMAGE_LIST_WIDGET_WIDTH)
        self.image_list_widget.itemClicked.connect(self.handle_image_list_widget_item_clicked)
        self.image_list_layout.addWidget(self.image_list_widget)
        self.image_list_group_box.setLayout(self.image_list_layout)
        self.layout.addWidget(self.image_list_group_box)

    def open_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder_path:
            self.load_images_from_folder(folder_path)

    def load_images_from_folder(self, folder_path):
        self.image_paths = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if
                            f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        if not self.image_paths:
            LOGGER().warning("No images found in the selected folder.")
            QMessageBox.warning(self, "No Images Found", "No images found in the selected folder.")
            return
        self.image_list_widget.clear()
        self.timepoints.clear()

        # Remove all widgets from the stack
        while self.blob_detector_stack.count() > 0:
            self.blob_detector_stack.removeWidget(self.blob_detector_stack.widget(0))

        progress_dialog = self.show_progress_dialog(len(self.image_paths), "Loading Images...", "Cancel")
        QApplication.processEvents()

        for i, image_path in enumerate(self.image_paths):
            blob_detector_ui = BlobDetectorUI(image_path, image_set_reader=self)
            self.blob_detector_stack.addWidget(blob_detector_ui)
            self.add_to_image_list(blob_detector_ui.blob_detector_logic)
            progress_dialog.setValue(i + 1)
            QApplication.processEvents()
        progress_dialog.close()
        self.update_image_list()
        if self.timepoints:
            self.export_button.setEnabled(True)
            self.export_to_excel_button.setEnabled(True)
            self.update_all_button.setEnabled(True)
        QApplication.processEvents()

    def handle_image_list_widget_item_clicked(self, item):
        selected_index = self.image_list_widget.row(item) # Get the index of item just clicked on
        # Set the current index of the StackedWidget to the newly selected index
        # This displays the proper BlobDetectorUI widget
        self.blob_detector_stack.setCurrentIndex(selected_index)
        current_widget = self.blob_detector_stack.currentWidget()
        if isinstance(current_widget, BlobDetectorUI):
            current_widget.update_display_image() # Update the displayed image for the selected BlobDetectorUI widget

    def show_progress_dialog(self, max_value, message, cancel_button_text):
        progress_dialog = QProgressDialog(message, cancel_button_text, 0, max_value, self)
        progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        progress_dialog.setValue(0)
        progress_dialog.show()
        # logging.debug("Progress dialog initialized and shown")
        return progress_dialog

    def count_all_blobs(self):
        # Update universal settings
        min_area = int(self.min_area_input.text())
        max_area = int(self.max_area_input.text())
        min_circularity = float(self.min_circularity_input.text()) / 100.0
        min_convexity = float(self.min_convexity_input.text()) / 100.0
        min_inertia_ratio = float(self.min_inertia_ratio_input.text()) / 100.0
        min_dist_between_blobs = int(self.min_dist_between_blobs_input.text())
        min_threshold = int(self.min_threshold_input.text())
        max_threshold = int(self.max_threshold_input.text())
        apply_gaussian_blur = self.gaussian_blur_checkbox.isChecked()
        apply_morphological_operations = self.morphological_operations_checkbox.isChecked()
        i = self.blob_detector_stack.count() - 1
        while i >= 0:
            cur_logic = self.blob_detector_stack.widget(i).blob_detector_logic
            if cur_logic.image_path is None:
                self.blob_detector_stack.removeWidget(cur_logic)
                self.image_list_widget.takeItem(i)
                logging.debug("Image list widget removed at index: %s", i)
            i -= 1
        self.progress_dialog = self.show_progress_dialog(self.blob_detector_stack.count() + 1, "Counting Blobs...",
                                                         "Cancel")
        self.progress_dialog.setAutoClose(False)
        self.progress_dialog.setAutoReset(False)
        self.progress_dialog.setValue(0)
        QApplication.processEvents()

        self.threads = []
        self.workers = []
        self.completed_tasks = 0

        def update_progress():
            self.completed_tasks += 1
            self.progress_dialog.setValue(self.completed_tasks)
            QApplication.processEvents()

        for i in range(self.blob_detector_stack.count()):
            ui = self.blob_detector_stack.widget(i)
            ui = ui if isinstance(ui, BlobDetectorUI) else None
            logic = ui.blob_detector_logic
            if logic.image_path is None:
                continue
            worker = BlobCounterWorker(logic, min_area, max_area, min_circularity, min_convexity, min_inertia_ratio,
                                       min_dist_between_blobs, min_threshold, max_threshold, apply_gaussian_blur,
                                       apply_morphological_operations)
            thread = QThread()
            worker.moveToThread(thread)
            worker.progress.connect(update_progress)
            worker.finished.connect(thread.quit)
            worker.finished.connect(worker.deleteLater)
            thread.finished.connect(thread.deleteLater)
            worker.error.connect(lambda e: logging.error(f"Error counting blobs: {e}"))
            thread.started.connect(worker.run)
            self.threads.append(thread)
            self.workers.append(worker)
            thread.start()

        start_time = time()
        timeout = 60  # Timeout in seconds

        while self.progress_dialog.isVisible():
            sleep(0.01)
            QApplication.processEvents()
            if self.completed_tasks >= self.blob_detector_stack.count():
                self.update_displayed_blob_counts_finished_loading()
                self.progress_dialog.setValue(self.progress_dialog.value() + 1)
                logging.debug("All tasks completed, closing progress dialog.")
                self.progress_dialog.close()
                break
            if time() - start_time > timeout:
                logging.warning("Timeout reached, forcing progress dialog to close.")
                self.progress_dialog.close()
                break

    def __update_displayed_blob_counts__(self):
        for i in range(self.blob_detector_stack.count()):
            widget = self.blob_detector_stack.widget(i)
            if isinstance(widget, BlobDetectorUI):
                if i >= self.blob_detector_stack.count():
                    continue
                blob_detector_logic = self.blob_detector_stack.widget(i).blob_detector_logic
                if blob_detector_logic.image_path is None:
                    continue
                list_name = blob_detector_logic.get_custom_name(DEFAULT_DILUTION)
                widget.update_display_image()
                if len(blob_detector_logic.keypoints) > 0:
                    self.image_list_widget.item(i).setText(f"{list_name} - Keypoints: {len(blob_detector_logic.keypoints)}")

    def update_all_displayed_blob_counts(self):
        if self.currently_updating:
            return
        self.__update_displayed_blob_counts__()

    def update_displayed_blob_count(self, keypoints_length):
        index = self.blob_detector_stack.indexOf(self.blob_detector_stack.currentWidget())
        if index == -1:
            return
        list_name = self.blob_detector_stack.widget(index).blob_detector_logic.get_custom_name(DEFAULT_DILUTION)
        self.image_list_widget.item(index).setText(f"{list_name} - Keypoints: {keypoints_length}")

    def update_displayed_blob_counts_finished_loading(self):
        self.currently_updating = True
        self.__update_displayed_blob_counts__()
        QApplication.processEvents()
        self.currently_updating = False


    def add_to_image_list(self, blob_detector_logic):
        list_name = blob_detector_logic.get_custom_name(DEFAULT_DILUTION)
        self.image_list_widget.addItem(f"{list_name}")
        self.timepoints.append(blob_detector_logic.get_timepoint())

    def extract_sample_number(self, item_text):
        parts = item_text.split(' ')
        for part in parts:
            if part.startswith("Sample") and part[6:].isdigit():
                return int(part[6:])
        return -1  # Default value if no sample number is found

    def update_image_list(self):
        old_selected_index = self.image_list_widget.selectedIndexes()[
            0].row() if self.image_list_widget.selectedIndexes() else 0
        timepoints_with_widgets = []
        for i in range(self.blob_detector_stack.count()):
            widget = self.blob_detector_stack.widget(i)
            if isinstance(widget, BlobDetectorUI):
                widget.blob_detector_logic.update_timepoint()
                timepoints_with_widgets.append((widget.blob_detector_logic.get_timepoint(), widget))
        # Sort timepoints and widgets by sample number
        timepoints_with_widgets.sort(key=lambda x: x[0].sample_number if x[0] else math.inf)

        # Re-order widgets in the StackedWidget and in the Image List Widget and the timepoints list - these shoudld always be ordered the same
        # Clear the Image List Widget and the list of timepoints first
        self.image_list_widget.clear()
        self.timepoints = []
        for _, (timepoint, widget) in enumerate(timepoints_with_widgets):
            # Start by removing every single widget - we want to add them all back in the correct order
            self.blob_detector_stack.removeWidget(widget)
        # Add the widgets back in the correct order to both the StackedWidget and the Image List Widget
        for _, (timepoint, widget) in enumerate(timepoints_with_widgets):
            self.blob_detector_stack.addWidget(widget)
            list_name = widget.blob_detector_logic.get_custom_name(DEFAULT_DILUTION)
            self.image_list_widget.addItem(f"{list_name}")
            self.timepoints.append(timepoint)

        # Ensure the correct widget is selected
        self.image_list_widget.setCurrentRow(old_selected_index)
        self.blob_detector_stack.setCurrentIndex(old_selected_index)

    def export_to_excel(self):
        if not self.timepoints:
            return
        # Update timepoints with the latest keypoint counts, should be redundant
        self.timepoints.clear()
        for i in range(self.blob_detector_stack.count()):
            widget = self.blob_detector_stack.widget(i)
            if isinstance(widget, BlobDetectorUI):
                widget.blob_detector_logic.update_timepoint()
                self.timepoints.append(widget.blob_detector_logic.get_timepoint())
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Blob Counts", "", "Excel Files (*.xlsx)")
        if not file_path:
            return
        excel_output = ExcelOutput(file_path)
        for timepoint in self.timepoints:
            if timepoint is not None:
                excel_output.write_blob_counts(timepoint.day, timepoint.sample_number, timepoint.num_keypoints)
        excel_output.save()
        logging.info(f"SUCCESS: Blob counts exported to Excel and saved to disk in file: \"{file_path}\".")

    def export_counted_images(self):
        self.save_all_keypoints_as_xml()
        logging.info(
            f"About to save counted images to disk, this may take a while...\".")
        day = -1
        for timepoint in self.timepoints:
            if timepoint is not None and timepoint.day != -1:
                if day == -1:
                    day = timepoint.day
                self.save_image_with_keypoints(timepoint)
        day_folder = os.path.join("counted_images", f"Day {day}")
        logging.info(
            f"SUCCESS: Images with counted keypoints saved to disk in folder: \"{os.path.join(day_folder, 'counted_images')}\".")

    def save_image_with_keypoints(self, timepoint):
        day_folder = os.path.join("counted_images", f"Day {timepoint.day}")
        os.makedirs(day_folder, exist_ok=True)
        for i in range(self.blob_detector_stack.count()):
            widget = self.blob_detector_stack.widget(i)
            if isinstance(widget, BlobDetectorUI) and widget.blob_detector_logic.get_timepoint().filename == timepoint.filename:
                image_with_keypoints = widget.blob_detector_logic.get_display_image()
                image_path = os.path.join(day_folder, f"{timepoint.filename=}.png") if timepoint.sample_number == -1 \
                    else os.path.join(day_folder, f"Sample_{timepoint.sample_number}.png")
                cv2.imwrite(image_path, image_with_keypoints)  # Save without converting to BGR
                break

    def save_all_keypoints_as_xml(self):
        root = ET.Element("Keypoints")
        day_element = None
        for i in range(self.blob_detector_stack.count()):
            widget = self.blob_detector_stack.widget(i)
            if isinstance(widget, BlobDetectorUI):
                keypoints = widget.blob_detector_logic.keypoints
                timepoint = widget.blob_detector_logic.get_timepoint()
                if timepoint is None:
                    continue
                if day_element is None or day_element.get("number") != str(timepoint.day):
                    day_element = ET.SubElement(root, "Day")
                    day_element.set("number", str(timepoint.day))
                sample_element = ET.SubElement(day_element, "Sample")
                if timepoint.sample_number == -1:
                    sample_element.set("filename", timepoint.filename)
                else:
                    sample_element.set("number", str(timepoint.sample_number))
                for keypoint in keypoints:
                    kp_element = ET.SubElement(sample_element, "Keypoint")
                    ET.SubElement(kp_element, "X").text = str(keypoint.pt[0])
                    ET.SubElement(kp_element, "Y").text = str(keypoint.pt[1])
                    ET.SubElement(kp_element, "Size").text = str(keypoint.size)

        xml_dir_path = os.path.join("counted_images", f"Day {timepoint.day}")
        os.makedirs(xml_dir_path, exist_ok=True)  # Ensure the directory exists
        xml_path = os.path.join(xml_dir_path, "keypoints.xml")

        # Pretty print the XML
        xml_str = ET.tostring(root, encoding='utf-8')
        parsed_xml = xml.dom.minidom.parseString(xml_str)
        pretty_xml_str = parsed_xml.toprettyxml(indent="  ")

        with open(xml_path, "w") as f:
            f.write(pretty_xml_str)
        logging.info(f"SUCCESS: Keypoints exported to XML and saved to disk at path: \"{xml_path}\".")