import logging
from PySide6.QtCore import QObject, Signal

class BlobCounterWorker(QObject):
    finished = Signal()
    error = Signal(str)
    progress = Signal(int)

    def __init__(self, logic, min_area, max_area, min_circularity, min_convexity, min_inertia_ratio,
                 min_dist_between_blobs, min_threshold, max_threshold, apply_gaussian_blur, apply_morphological_operations):
        super().__init__()
        self.logic = logic
        self.min_area = min_area
        self.max_area = max_area
        self.min_circularity = min_circularity
        self.min_convexity = min_convexity
        self.min_inertia_ratio = min_inertia_ratio
        self.min_dist_between_blobs = min_dist_between_blobs
        self.min_threshold = min_threshold
        self.max_threshold = max_threshold
        self.apply_gaussian_blur = apply_gaussian_blur
        self.apply_morphological_operations = apply_morphological_operations

    def run(self):
        try:
            self.logic.update_blob_count(
                self.min_area, self.max_area, self.min_circularity, self.min_convexity, self.min_inertia_ratio,
                self.min_dist_between_blobs, self.apply_gaussian_blur, self.apply_morphological_operations,
                self.min_threshold, self.max_threshold
            )
            self.progress.emit(1)  # Emit progress signal
        except Exception as e:
            logging.error(f"Error in BlobCounterWorker: {e}")
            self.error.emit(str(e))
        finally:
            self.finished.emit()