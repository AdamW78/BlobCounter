import logging

import cv2
import torch
from ultralytics import YOLO


class BlobCounterBase:
    def __init__(self):
        pass

    def count_blobs(self, image, **kwargs):
        raise NotImplementedError("count_blobs must be implemented by subclasses.")


class YOLOBlobCounter(BlobCounterBase):
    def __init__(self, model_path):
        # device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        # logging.info(f"Using device: {device}")
        super().__init__()

        self.model = YOLO(model_path)
        self.model.to(torch.device("cpu"))

    def count_blobs(self, image, **kwargs):
        # Ensure image is RGB
        logging.info("Running YOLO inference on image...")

        if image.ndim == 2:
            img_rgb = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        elif image.shape[2] == 3:
            img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        else:
            raise ValueError("Unsupported image shape for YOLO inference.")

        # Run YOLO inference
        results = self.model.predict(source=img_rgb, verbose=False)
        keypoints = []

        # Handle results
        if not results or not hasattr(results[0], "boxes") or results[0].boxes is None:
            return keypoints

        boxes = results[0].boxes
        xywh = boxes.xywh.cpu().numpy() if hasattr(boxes, "xywh") else []

        for x_center, y_center, w, h in xywh:
            size = max(w, h)
            keypoints.append(cv2.KeyPoint(float(x_center), float(y_center), float(size)))
        return keypoints