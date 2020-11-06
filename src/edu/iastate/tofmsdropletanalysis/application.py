import sys
import time
import Queue

import cv2
from PyQt5 import QtWidgets, Qt
from PyQt5 import uic
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot, QPoint, QTimer
from PyQt5.QtGui import QImage, QPixmap, QFont, QPainter
from PyQt5.QtWidgets import QWidget, QMessageBox
from PyQt5.uic.properties import QtGui, QtCore

from edu.iastate.tofmsdropletanalysis.microdrop import Microdrop
from edu.iastate.tofmsdropletanalysis.test_application import get_all_drops

m = Microdrop()

running = False
capture_thread = None
q = Queue


def grab(cam, queue, width, height, fps):
    global running
    capture = cv2.VideoCapture(cam)
    capture.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    capture.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    capture.set(cv2.CAP_PROP_FPS, fps)

    while (running):
        frame = {}
        capture.grab()
        retval, img = capture.retrieve(0)
        frame["img"] = img

        if queue.qsize() < 10:
            queue.put(frame)
        else:
            print
            queue.qsize()


class ImageWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        super(ImageWidget, self).__init__(parent)
        self.image = None

    def setImage(self, image):
        self.image = image
        sz = image.size()
        self.setMinimumSize(sz)
        self.update()

    def paintEvent(self, event):
        qp = QtGui.QPainter()
        qp.begin(self)
        if self.image:
            qp.drawImage(QtCore.QPoint(0, 0), self.image)
        qp.end()


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # load in GUI from qtDesigner in '.ui' format. Must be in same directory as .py file
        uic.loadUi("ui/main_gui.ui", self)

        self._init()

    # Connect Qt UI handlers.
    def _init(self):
        # Start and Stop
        self.pushButton_drops.clicked.connect(self.tripledrops_clicked)
        self.pushButton_camera.clicked.connect(self.camera_clicked)

        # Voltage
        self.spinBoxV1.valueChanged.connect(self.change_triplevoltage)
        self.spinBoxV2.valueChanged.connect(self.change_triplevoltage)
        self.spinBoxV3.valueChanged.connect(self.change_triplevoltage)

        # Pulse Width
        self.doubleSpinBoxPWidth1.valueChanged.connect(self.change_triplepulselength)
        self.doubleSpinBoxPWidth2.valueChanged.connect(self.change_triplepulselength)
        self.doubleSpinBoxPWidth3.valueChanged.connect(self.change_triplepulselength)

        # Pulse Delay
        self.doubleSpinBoxPDelay1.valueChanged.connect(self.change_triplepulsedelay)
        self.doubleSpinBoxPDelay2.valueChanged.connect(self.change_triplepulsedelay)
        self.doubleSpinBoxPDelay2.valueChanged.connect(self.change_triplepulsedelay)

        # Frequency
        self.spinBoxFreq.valueChanged.connect(self.change_freqtriple)

        # Drops
        self.spinBoxDrops.valueChanged.connect(self.change_dropstriple)

        self.startButton.clicked.connect(self.start_camera)
        self.stopButton.clicked.connect(self.stop_camera)

        self.ImgWidget = ImageWidget(self.ImgWidget)

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(1)

    ########################################################################
    # connecting functions to GUI. "set" functions encode the numbers
    # in the correct byte format for the MDG. "change" functions change the
    # value in the GUI itself and send it to the MDG.
    ########################################################################

    def tripledrops_clicked(self):
        # actions when button is clicked
        if self.pushButton_drops.isChecked():
            m.flush()
            self.pushButton_drops.setText("Stop Droplets")  # change button text to "stop droplets")
            m.turn_dispenser_on()  # Start MDG

            ### timing filter to prevent double signals from button
            while True:
                self.pushButton_drops.clicked.disconnect(self.tripledrops_clicked)
                time.sleep(0.2)

                break
            self.pushButton_drops.clicked.connect(self.tripledrops_clicked)
            m.flush()


        # actions when button is not clicked
        else:
            m.flush()
            self.pushButton_drops.setText("Start Droplets")  # change text back to "start drop
            m.turn_dispenser_off()  # Stop MDG

    ###### THIS IS NOT FINISHED!!!! make sure to add time filter

    def camera_clicked(self):
        # actions when button is clicked
        if self.pushButton_camera.isChecked():
            self.pushButton_camera.setText("Stop Camera")  # change button text to "stop camera"

        # actions when button is not clicked
        else:
            self.pushButton_camera.setText("Start Camera")  # change text back to "start camera"

    ####voltage####

    def change_triplevoltage(self):
        v1 = self.spinBoxV1.value()
        v2 = self.spinBoxV2.value()
        v3 = self.spinBoxV3.value()

        m.set_voltage1(v1)
        m.set_voltage2(v2)
        m.set_voltage3(v3)

    ####pulsewidth####
    def change_triplepulselength(self):
        pw1 = self.doubleSpinBoxPWidth1.value()
        pw2 = self.doubleSpinBoxPWidth2.value()
        pw3 = self.doubleSpinBoxPWidth3.value()

        m.set_pulse_length1(pw1)
        m.set_pulse_length2(pw2)
        m.set_pulse_length3(pw3)

    ####pulse delay####
    def change_triplepulsedelay(self):
        pd1 = self.doubleSpinBoxPDelay1.value()
        pd2 = self.doubleSpinBoxPDelay2.value()
        pd3 = self.doubleSpinBoxPDelay3.value()

        m.set_pulsedelay1(pd1)
        m.set_pulsedelay2(pd2)
        m.set_pulsedelay3(pd3)

    ####freq and burst####
    def change_freqtriple(self):
        freq = self.spinBoxFreq.value()
        m.set_freq(freq)

    def change_dropstriple(self):
        drops = self.spinBoxDrops.value()
        m.set_drops(drops)

    def start_camera(self):
        pass

    def stop_camera(self):
        pass


# call this last to execute app
def main():
    # create inst of application
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    # show GUI and execute app
    window.show()
    app.exec()


if __name__ == "__main__":
    main()
