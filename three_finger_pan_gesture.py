from PySide6.QtCore import QPointF, QEvent, Qt
from PySide6.QtWidgets import QGesture, QGestureRecognizer


class ThreeFingerPanGesture(QGesture):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._delta = QPointF()
        self._last_offset = QPointF()
        self._offset = QPointF()

    def delta(self):
        return self._delta

    def lastOffset(self):
        return self._last_offset

    def offset(self):
        return self._offset

    def setDelta(self, value):
        self._delta = value

    def setLastOffset(self, value):
        self._last_offset = value

    def setOffset(self, value):
        self._offset = value


from PySide6.QtCore import QEvent, Qt, QPointF
from PySide6.QtWidgets import QGestureRecognizer

class ThreeFingerPanGestureRecognizer(QGestureRecognizer):
    def __init__(self):
        super().__init__()
        self.amplification_factor = 2.0  # Adjust this factor to increase sensitivity

    def create(self, target):
        return ThreeFingerPanGesture(target)

    def recognize(self, gesture, watched, event):
        if not isinstance(gesture, ThreeFingerPanGesture):
            return QGestureRecognizer.ResultFlag.CancelGesture

        if event.type() == QEvent.Type.TouchBegin:
            if len(event.touchPoints()) == 3:
                gesture.setLastOffset(QPointF())
                gesture.setOffset(QPointF())
                gesture.setDelta(QPointF())
                gesture.state = Qt.GestureState.GestureStarted
                return QGestureRecognizer.ResultFlag.MayBeGesture
            else:
                return QGestureRecognizer.ResultFlag.CancelGesture

        elif event.type() == QEvent.Type.TouchUpdate:
            if len(event.touchPoints()) == 3:
                current_pos = event.touchPoints()[0].pos()
                start_pos = event.touchPoints()[0].startPos()
                last_offset = gesture.offset()
                new_offset = current_pos - start_pos
                delta = (new_offset - last_offset) * self.amplification_factor
                gesture.setLastOffset(last_offset)
                gesture.setOffset(new_offset)
                gesture.setDelta(delta)
                gesture.state = Qt.GestureState.GestureUpdated
                return QGestureRecognizer.ResultFlag.TriggerGesture
            else:
                return QGestureRecognizer.ResultFlag.CancelGesture

        elif event.type() == QEvent.Type.TouchEnd:
            if gesture.state == Qt.GestureState.GestureUpdated:
                gesture.state = Qt.GestureState.GestureFinished
                return QGestureRecognizer.ResultFlag.FinishGesture
            else:
                return QGestureRecognizer.ResultFlag.CancelGesture

        return QGestureRecognizer.ResultFlag.Ignore

    def reset(self, gesture):
        if isinstance(gesture, ThreeFingerPanGesture):
            gesture.setDelta(QPointF())
            gesture.setLastOffset(QPointF())
            gesture.setOffset(QPointF())
        super().reset(gesture)
