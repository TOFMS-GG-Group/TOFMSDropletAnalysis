import time


class SerialDevice:

    def __init__(self, port):
        self._port = port

    def send(self, cmd):
        self._port.flush()
        self._port.write((cmd + '\r').encode())

        # Time Filter
        time.sleep(0.00001)

    # TODO This is not finished to be in the right format.
    def receive(self, cmd):
        self._port.flush()
        self._port.write((cmd + '\r').decode())
        ret = self._port.readline().receive().strip()
        while ret.startswith('>'):
            ret = ret[1:]

        if ret == '':
            return 0
        else:
            return float(ret)

    def flush(self):
        self._port.flush()

#
# def microdrop_manualVoltageSet(voltage, device=Microdrop, head=1):
#     # print('change MDG1')
#     device.voltage1 = voltage
#     device.voltage2 = 0
#     device.voltage3 = 0
#
#
# def microdrop_manualPulseSet(pulse, device=Microdrop, head=1):
#     device.pulsewidth1 = pulse
#     device.pulsewidth2 = 0
#     device.pulsewidth3 = 0
#
#
#
#
# def microdrop_change_volt_val(self):
#    microdrop_manualVoltageSet(self.voltage.value(), self._microDrop, head=self._display)
#
# microdrop_manualVoltageSet(20)
