import sys
import random as rand

from PyQt5.QtWidgets import QApplication, QMainWindow, QRubberBand, QLabel
from PyQt5.QtGui import QPixmap, QColor, QPainter, QMouseEvent, QPolygon
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QThread, QPoint, QRect, QSize


def create_pixmap():
    def color():
        r = 255
        g = 0
        b = 50

        return QColor(r, g, b)

    def point():
        return QPoint(rand.randrange(0, 400), rand.randrange(0, 300))

    pixmap = QPixmap(400, 300)
    pixmap.fill(color())
    painter = QPainter()
    painter.begin(pixmap)
    i = 0

    while i < 1000:
        painter.setBrush(color())
        painter.drawPolygon(QPolygon([point(), point(), point()]))
        i += 1

    painter.end()
    return pixmap


class Window(QLabel):
    def __int__(self, parent=None):
        QLabel.__init__(self, parent)

        self.rubberBand = QRubberBand(QRubberBand.Rectangle, self)
        self.origin = QPoint()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.origin = QPoint(event.pos())
            self.rubberBand.setGeometry(QRect(self.origin, QSize()))
            self.rubberBand.show()

    def mouseMoveEvent(self, event: QMouseEvent):
        if not self.origin.isNull():
            self.rubberBand.setGeometry(QRect(self.origin, event.pos()).normalized())

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.rubberBand.hide()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    window.setPixmap(create_pixmap())
    window.resize(400, 300)
    window.show()
    sys.exit(app.exec_())
