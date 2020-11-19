import sys
import time

import cv2

from PyQt5 import QtGui, uic
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QThread

import numpy as np

from edu.iastate.tofmsdropletanalysis.vision import get_all_drops

# m = Microdrop()
m = None

# TODO: Update the params to find the only circle we care about.
def circle_detect(img):
    grey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    grey_blurred = cv2.blur(grey, (3, 3))

    detected_circles = cv2.HoughCircles(grey_blurred,
                                        cv2.HOUGH_GRADIENT, 1, 20, param1=50,
                                        param2=30, minRadius=1, maxRadius=40)

    if detected_circles is not None:
        detected_circles = np.uint16(np.around(detected_circles))

        for pt in detected_circles[0, :]:
            a, b, r = pt[0], pt[1], pt[2]

            cv2.circle(img, (a, b), r, (0, 255, 0), 2)

    return img


# TODO Change to use the XiCam API.
# TODO Handle the Droplet Analysis.
class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)

    def __init__(self):
        super().__init__()
        self._run_flag = True

    def run(self):
        cap = cv2.VideoCapture(0)

        while self._run_flag:
            ret, cv_img = cap.read()
            
            if ret:
                cv_img = circle_detect(cv_img)

                self.change_pixmap_signal.emit(cv_img)
            else:
                # TODO This code is only for looping the sample video.
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)


        cap.release()

    def stop(self):
        self._run_flag = False
        self.wait()


class App(QMainWindow):
    def __init__(self):
        super().__init__()

        uic.loadUi("ui/main_gui.ui", self)

        self.setWindowTitle("TOFMS Drop Analysis")

        self.display_width = 640
        self.display_height = 480

        self.ImgWidget.resize(self.display_width, self.display_height)

        self.thread = VideoThread()

        self.thread.change_pixmap_signal.connect(self.update_image)
        self.thread.start()

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

    def closeEvent(self, event):
        self.thread.stop()
        event.accept()

    @pyqtSlot(np.ndarray)
    def update_image(self, cv_img):
        qt_img = self.convert_cv_qt(cv_img)
        self.ImgWidget.setPixmap(qt_img)

    def convert_cv_qt(self, cv_img):
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(self.display_width, self.display_height, Qt.KeepAspectRatio)

        return QPixmap.fromImage(p)

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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    a = App()
    a.show()
    sys.exit(app.exec_())
