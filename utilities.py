import utime
from machine import Pin

class LED():
    def __init__(self, pin):
        self.led = Pin(pin, Pin.OUT)

    def on(self, duration=None):
        """
        Turn led off
        :param duration: Time in seconds to remain off (optional)
        """
        self.led.value(1)
        if duration:
            utime.sleep(duration)
            self.off()

    def off(self, duration=None):
        """
        Turn led off
        :param duration: Time in seconds to remain off (optional)
        """
        self.led.value(0)
        if duration:
            utime.sleep(duration)
            self.on()

    def blink(self, rate=1, duration=None):
        """
        Blink LED at a specified rate.
        :param rate: Time in seconds between toggles.
        :param duration: Total duration to blink the LED (optional).
        """
        end_time = utime.time() + duration if duration else None
        while duration is None or utime.time() < end_time:
            self.led.value(not self.led.value())
            utime.sleep(rate)
