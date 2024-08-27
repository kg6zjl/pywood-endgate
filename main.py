"""
PyWood is tracking the order of derby cars crossing the end gate.
For this use case, we don't care about timing the cars.
A reset button is pressed to clear the displays and resume
"""

import time
import tm1637
from machine import Pin

# map out each lane to ldr sensor, add more lanes/sensors here
LDR_PIN_MAP = {
    15: {"lane": 1},
    16: {"lane": 2},
    17: {"lane": 3},
    18: {"lane": 4},
}

# Constants
RESET_BTN_PIN = Pin(15, Pin.IN, Pin.PULL_UP)
LDR_PINS = list(LDR_PIN_MAP.keys())
TM_PINS = [(5, 4), (5, 5)]
BLANK_DISPLAY = [0x00, 0x00, 0x00, 0x00]
LANE_COUNT = len(LDR_PINS)

# Initialize LDR sensors and TM1637 displays
LDR_SENSORS = [Pin(pin, Pin.IN) for pin in LDR_PINS]
TM_DRIVERS = [tm1637.TM1637(clk=Pin(clk), dio=Pin(dio)) for clk, dio in TM_PINS]

# Global variables
RANK = []
STOP_DISPLAY_UPDATES = False

def check_reset_button():
    global RANK, STOP_DISPLAY_UPDATES
    if RESET_BTN_PIN.value() == 0:
        segment_display_handler(BLANK_DISPLAY)
        # reset for next race
        RANK = []
        # resume display updates
        STOP_DISPLAY_UPDATES = False
        time.sleep(0.1)  # Debounce delay

def segment_display_handler(content):
    for driver in TM_DRIVERS:
        driver.write(content)
    time.sleep(0.01)

def check_ldr_sensors():
    global RANK
    for i, ldr_pin in enumerate(LDR_SENSORS):
        lane = LDR_PIN_MAP[ldr_pin]['lane']
        if ldr_pin.value() == 1 and (lane) not in RANK:
            RANK.append(lane)
    time.sleep(0.01)  # Debounce delay

# Initialize displays on first start
segment_display_handler(BLANK_DISPLAY)

# Main loop to check sensors and update display
while True:
    # check sensors
    check_ldr_sensors()
    # if a sensor has registered, start updating display
    if RANK and not STOP_DISPLAY_UPDATES:
        segment_display_handler(RANK)
    # once the last place registers, we can stop updating the
    # display on each cycle until the reset button is pressed
    if len(RANK) == LANE_COUNT:
        STOP_DISPLAY_UPDATES = True
    # check if reset button is pressed
    check_reset_button()
