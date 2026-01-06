from ctypes import cdll
from app.utils.logging import device_logger

lib = cdll.LoadLibrary("/home/guillaume/SCA-Studio/Install 1.9.20/bps202.dll")

class Injector:
    def __init__(self):
        name="bps202"
        self._alternate=0
        self._burst_period=10
        self._pulse_counter=0
        self._burst_counter=0
        self._counter_mode=0
        self._pulse_range_index=0
        self._pulse_level_index=0
        self._pulse_polarity=0
        self._pulse_burst_mode=0
        self._pulse_period=1000
        self._pulses_per_burst=10
        self._trigger_config_mode=[0,1,0,0]
        self._trigger_delay=10
        self._low_jitter_trigger_delay=0
        self._control=1

    @device_logger
    def connect(self):
        lib.bps_init()
        while lib.bps_get_status()<0:
            pass

    @device_logger
    def disconnect(self):
        lib.bps_close()

    def set_control(self,control):
        if control in [1,2]:
            self._control=control

    def get_alternate(self):
        return self._alternate

    def set_alternate(self, value):
        self._alternate = value

    def get_burst_period(self):
        return self._burst_period

    def set_burst_period(self, value):
        self._burst_period = value

    def get_pulse_counter(self):
        return self._pulse_counter

    def set_pulse_counter(self, value):
        self._pulse_counter = value

    def get_burst_counter(self):
        return self._burst_counter

    def set_burst_counter(self, value):
        self._burst_counter = value

    def get_counter_mode(self):
        return self._counter_mode

    def set_counter_mode(self, value):
        self._counter_mode = value

    def get_pulse_range_index(self):
        return self._pulse_range_index

    def set_pulse_range_index(self, value):
        self._pulse_range_index = value

    def get_pulse_level_index(self):
        return self._pulse_level_index

    def set_pulse_level_index(self, value):
        self._pulse_level_index = value

    def get_pulse_polarity(self):
        return self._pulse_polarity

    def set_pulse_polarity(self, value):
        self._pulse_polarity = value

    def get_pulse_burst_mode(self):
        return self._pulse_burst_mode

    def set_pulse_burst_mode(self, value):
        self._pulse_burst_mode = value

    def get_pulse_period(self):
        return self._pulse_period

    def set_pulse_period(self, value):
        self._pulse_period = value

    def get_pulses_per_burst(self):
        return self._pulses_per_burst

    def set_pulses_per_burst(self, value):
        self._pulses_per_burst = value

    def get_trigger_config_mode(self):
        return self._trigger_config_mode

    def set_trigger_config_mode(self, value):
        self._trigger_config_mode = value

    def get_trigger_delay(self):
        return self._trigger_delay

    def set_trigger_delay(self, value):
        self._trigger_delay = value

    def get_low_jitter_trigger_delay(self):
        return self._low_jitter_trigger_delay

    def set_low_jitter_trigger_delay(self, value):
        self._low_jitter_trigger_delay = value

    def get_control(self):
        return self._control

    @device_logger
    def send_injection(self):
        lib.bps_control(self._control)
        while lib.bps_get_status()<1:
            pass
        #measure....
        lib.bps_control(0)
        while lib.bps_get_status()>0:
            pass