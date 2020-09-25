import sys
import time

from PyQt5 import QtWidgets
from PyQt5 import uic

from edu.iastate.tofmsdropletanalysis.microdrop import Microdrop

m = Microdrop()


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # load in GUI from qtDesigner in '.ui' format. Must be in same directory as .py file
        uic.loadUi("MDG_gui_NEWTAB.ui", self)

        self._connect_handlers()

    #########################################
    ############## Handlers #################
    #########################################

    # connect names of widgets to functions that give them actions
    def _connect_handlers(self):

        ### start/stop
        self.pushButton_drops.clicked.connect(self.tripledrops_clicked)
        self.pushButton_camera.clicked.connect(self.camera_clicked)

        ########### triple pulse ###########
        # voltage
        self.spinBoxV1.valueChanged.connect(self.change_triplevoltage)
        self.spinBoxV2.valueChanged.connect(self.change_triplevoltage)
        self.spinBoxV3.valueChanged.connect(self.change_triplevoltage)

        # pulse width
        self.doubleSpinBoxPWidth1.valueChanged.connect(self.change_triplepulselength)
        self.doubleSpinBoxPWidth2.valueChanged.connect(self.change_triplepulselength)
        self.doubleSpinBoxPWidth3.valueChanged.connect(self.change_triplepulselength)

        # pulse delay
        self.doubleSpinBoxPDelay1.valueChanged.connect(self.change_triplepulsedelay)
        self.doubleSpinBoxPDelay2.valueChanged.connect(self.change_triplepulsedelay)
        self.doubleSpinBoxPDelay2.valueChanged.connect(self.change_triplepulsedelay)

        # frequency
        self.spinBoxFreq.valueChanged.connect(self.change_freqtriple)

        # drops
        self.spinBoxDrops.valueChanged.connect(self.change_dropstriple)

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
