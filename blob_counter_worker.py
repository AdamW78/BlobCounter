import logging
from PySide6.QtCore import QObject, Signal

class BlobCounterWorker(QObject):
    finished = Signal()
    error = Signal(str)
    progress = Signal(int)

    def __init__(self, logic):
        super().__init__()
        self.logic = logic

    def run(self):
        try:
            self.logic.update_blob_count()
            self.progress.emit(1)  # Emit progress signal
        except Exception as e:
            logging.error(f"Error in BlobCounterWorker: {e}")
            self.error.emit(str(e))
        finally:
            self.finished.emit()