from PySide6.QtCore import Qt
from PySide6.QtWidgets import QSpacerItem, QSizePolicy, QSlider, QLabel, QHBoxLayout, QLineEdit, QVBoxLayout, QGroupBox

from utils import SLIDER_NAME_MIN_AREA, SLIDER_MIN_VALUE, DEFAULT_MAX_AREA, DEFAULT_MIN_AREA, TOOLTIP_MIN_AREA, \
    TOOLTIP_MAX_AREA, TOOLTIP_MIN_CIRCULARITY, DEFAULT_MIN_CIRCULARITY, SLIDER_MAX_VALUE, DEFAULT_MIN_CONVEXITY, \
    DEFAULT_MIN_INERTIA_RATIO, TOOLTIP_MIN_CONVEXITY, TOOLTIP_MIN_INERTIA_RATIO, TOOLTIP_MIN_DIST_BETWEEN_BLOBS, \
    DEFAULT_MIN_DIST_BETWEEN_BLOBS, TOOLTIP_MIN_THRESHOLD, TOOLTIP_MAX_THRESHOLD, DEFAULT_MIN_THRESHOLD, \
    DEFAULT_MAX_THRESHOLD, SLIDER_MAX_THRESHOLD_VALUE, SLIDER_NAME_MIN_THRESHOLD, SLIDER_NAME_MIN_DIST_BETWEEN_BLOBS, \
    SLIDER_NAME_MAX_THRESHOLD, SLIDER_NAME_MIN_INERTIA_RATIO, SLIDER_NAME_MIN_CONVEXITY, SLIDER_NAME_MIN_CIRCULARITY, \
    SLIDER_NAME_MAX_AREA


class UIUtils:
    @staticmethod
    def create_slider_with_input(name, min_value, max_value, initial_value, tooltip, is_percentage=False):
        group_box = QGroupBox()
        group_box.setStyleSheet("QGroupBox { border: 1px solid #555; border-radius: 4px; margin-top: 3px; }")

        layout = QVBoxLayout(group_box)
        layout.setContentsMargins(3, 3, 3, 3)
        layout.setSpacing(0)  # Set vertical spacing to zero

        # Create HBox for label and input field
        hbox = QHBoxLayout()
        label = QLabel(name)
        label.setObjectName("sliderTitleLabel")
        display_value = int(float(initial_value * 100)) if is_percentage else int(initial_value)
        input_field = QLineEdit(str(display_value))
        input_field.setFixedWidth(35)

        hbox.addWidget(label)
        hbox.addStretch()
        hbox.addWidget(input_field)

        layout.addLayout(hbox)
        slider_hbox = QHBoxLayout()
        min_label = QLabel(str(int(min_value * 100)) if is_percentage else str(int(min_value)))
        slider = QSlider(Qt.Horizontal)
        slider.setRange(min_value * 100 if is_percentage else min_value, max_value * 100 if is_percentage else max_value)
        slider.setValue(initial_value * 100 if is_percentage else initial_value)
        slider.setToolTip(tooltip)
        slider.setFixedHeight(15)
        max_label = QLabel(str(int(max_value * 100)) if is_percentage else str(int(max_value)))

        slider_hbox.addWidget(min_label)
        slider_hbox.addItem(QSpacerItem(10, 0, QSizePolicy.Fixed, QSizePolicy.Minimum))  # Add horizontal spacing
        slider_hbox.addWidget(slider)
        slider_hbox.addItem(QSpacerItem(10, 0, QSizePolicy.Fixed, QSizePolicy.Minimum))  # Add horizontal spacing
        slider_hbox.addWidget(max_label)

        layout.addLayout(slider_hbox)

        def update_input_field(value):
            display_value = value
            input_field.setText(str(int(display_value)))

        def update_slider():
            text = input_field.text()
            if text.isdigit():
                value = int(text)
                slider.setValue(value)
            else:
                display_value = slider.value()
                input_field.setText(str(int(display_value)))

        slider.valueChanged.connect(update_input_field)
        input_field.editingFinished.connect(update_slider)

        return group_box, slider, input_field

    @staticmethod
    def create_blob_detector_sliders():
        sliders = {}
        sliders['min_area'] = UIUtils.create_slider_with_input(SLIDER_NAME_MIN_AREA, SLIDER_MIN_VALUE, DEFAULT_MAX_AREA,
                                                               DEFAULT_MIN_AREA, TOOLTIP_MIN_AREA)
        sliders['max_area'] = UIUtils.create_slider_with_input(SLIDER_NAME_MAX_AREA, SLIDER_MIN_VALUE, DEFAULT_MAX_AREA,
                                                               DEFAULT_MAX_AREA, TOOLTIP_MAX_AREA)
        sliders['min_circularity'] = UIUtils.create_slider_with_input(
            SLIDER_NAME_MIN_CIRCULARITY, 0, 1, DEFAULT_MIN_CIRCULARITY, TOOLTIP_MIN_CIRCULARITY, is_percentage=True
        )
        sliders['min_convexity'] = UIUtils.create_slider_with_input(
            SLIDER_NAME_MIN_CONVEXITY, 0, 1, DEFAULT_MIN_CONVEXITY, TOOLTIP_MIN_CONVEXITY, is_percentage=True
        )
        sliders['min_inertia_ratio'] = UIUtils.create_slider_with_input(
            SLIDER_NAME_MIN_INERTIA_RATIO, 0, 1, DEFAULT_MIN_INERTIA_RATIO, TOOLTIP_MIN_INERTIA_RATIO, is_percentage=True
        )
        sliders['min_dist_between_blobs'] = UIUtils.create_slider_with_input(SLIDER_NAME_MIN_DIST_BETWEEN_BLOBS,
                                                                             SLIDER_MIN_VALUE, SLIDER_MAX_VALUE,
                                                                             DEFAULT_MIN_DIST_BETWEEN_BLOBS,
                                                                             TOOLTIP_MIN_DIST_BETWEEN_BLOBS)
        sliders['min_threshold'] = UIUtils.create_slider_with_input(SLIDER_NAME_MIN_THRESHOLD, SLIDER_MIN_VALUE,
                                                                    SLIDER_MAX_THRESHOLD_VALUE, DEFAULT_MIN_THRESHOLD,
                                                                    TOOLTIP_MIN_THRESHOLD)
        sliders['max_threshold'] = UIUtils.create_slider_with_input(SLIDER_NAME_MAX_THRESHOLD, SLIDER_MIN_VALUE,
                                                                    SLIDER_MAX_THRESHOLD_VALUE, DEFAULT_MAX_THRESHOLD,
                                                                    TOOLTIP_MAX_THRESHOLD)
        return sliders