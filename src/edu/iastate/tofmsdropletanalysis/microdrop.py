import os

from serial import Serial

from edu.iastate.tofmsdropletanalysis.serialdevice import SerialDevice


class Microdrop:
    serialDevice = None

    if os.name == 'posix':
        serialDevice = SerialDevice(Serial('/dev/tty.usbserial-AL05NLPZ', 19200))
    elif os.name == 'nt':
        serialDevice = SerialDevice(Serial('COM100', 19200))

    def __init__(self):
        pass

    def flush(self):
        self.serialDevice.flush()

    # LED Controls
    def set_strobe_delay(self, strobe_del):
        self.serialDevice.send('SetStrobe(1,' + str(strobe_del) + ')')

    def set_backlight(self, brightness):
        self.serialDevice.send('BackLight(1,' + str(brightness) + ')')

    def get_strobe(self):
        self.serialDevice.receive('GetStrobe(1)')

    # Voltage
    def set_voltage1(self, v1):
        self.serialDevice.send('SetPulseVoltage(1,1,' + str(v1) + ')')

    def set_voltage2(self, v2):
        self.serialDevice.send('SetPulseVoltage(1,2,' + str(v2) + ')')

    def set_voltage3(self, v3):
        self.serialDevice.send('SetPulseVoltage(1,3,' + str(v3) + ')')

    def get_voltage1(self):
        self.serialDevice.receive('GetPulseVoltage(1,1)')

    def get_voltage2(self):
        self.serialDevice.receive('GetPulseVoltage(1,2)')

    def get_voltage3(self):
        self.serialDevice.receive('GetPulseVoltage(1,3)')

    # Pulse Length
    def set_pulse_length1(self, pw1):
        self.serialDevice.send('SetPulseLength(1,1,' + str(pw1) + ')')

    def set_pulse_length2(self, pw2):
        self.serialDevice.send('SetPulseLength(1,2,' + str(pw2) + ')')

    def set_pulse_length3(self, pw3):
        self.serialDevice.send('SetPulseLength(1,3,' + str(pw3) + ')')

    def get_pulse_length1(self):
        self.serialDevice.receive('GetPulseLength(1,1)')

    def get_pulse_length2(self):
        self.serialDevice.receive('GetPulseLength(1,2)')

    def get_pulse_length3(self):
        self.serialDevice.receive('GetPulseLength(1,3)')

    ##### set pulse delay #####
    def set_pulsedelay1(self, pd1):
        self.serialDevice.send('SetPulseDelay(1,1,' + str(pd1) + ')')

    def set_pulsedelay2(self, pd2):
        self.serialDevice.send('SetPulseDelay(1,2,' + str(pd2) + ')')

    def set_pulsedelay3(self, pd3):
        self.serialDevice.send('SetPulseDelay(1,3,' + str(pd3) + ')')

    def get_pulsedelay1(self):
        self.serialDevice.receive('GetPulseDelay(1,1)')

    def get_pulsedelay2(self):
        self.serialDevice.receive('GetPulseDelay(1,2)')

    def get_pulsedelay3(self):
        self.serialDevice.receive('GetPulseDelay(1,3)')

    ##### turning on/off MDG #####
    def turn_dispenser_on(self):
        self.serialDevice.send('StartHead(1,1)')

    def turn_dispenser_off(self):
        self.serialDevice.send('StartHead(1,0)')

    ##### freq and burst drops #####

    # droplet frequency
    def set_freq(self, freq):
        self.serialDevice.send('SetFrequency(1,' + str(freq) + ')')

    # number of drops released
    def set_drops(self, drops):
        self.serialDevice.send('SetDrops(1,' + str(drops) + ')')

    ### trigger

    def set_trigger_ext(self):
        self.serialDevice.send('SetTrigger(1,2,2)')
        self.serialDevice.send('SetTrigger(1,15,128')
        self.serialDevice.send('SetTrigger(1,22,1)')
