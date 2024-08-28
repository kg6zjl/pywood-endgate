"""
PyWood is built to track the order of derby cars crossing the end gate.
For this use case, we don't care about timing the cars.
A reset button is pressed to clear the displays and reset for next heat.
"""

import utime
import tm1637
import networking
from utilities import LED
from lcd import Display
from machine import I2C, Pin
from lcd_i2c import LCD

# map out each lane to ldr sensor, add more lanes/sensors here
LDR_PIN_MAP = {
    15: {"lane": 1},
    16: {"lane": 2},
    17: {"lane": 3},
    18: {"lane": 4},
}

# Networking Config
WIFI_SSID = 'pinewood_derby'

######################################################
# Constants
######################################################
LDR_PINS = list(LDR_PIN_MAP.keys())
# CLOCK_PIN = Pin(5, Pin.OUT)
TM_PINS = [(5, 4), (5, 5)] # can append more 7-segment displays
BLANK_DISPLAY = [0x00, 0x00, 0x00, 0x00]
LANE_COUNT = len(LDR_PINS)
LCD_PIN_SCL = 20
LCD_PIN_SDA = 21
LCD_ADDRESS = 0x27
RESET_BUTTON_PIN = 15
STATUS_LED_PIN = 22

######################################################
# Initialize sensors, displays, buttons, etc (in/out)
######################################################
# loop over LDR sensor map
LDR_SENSORS = [Pin(pin, Pin.IN) for pin in LDR_PINS]
# loop over and intialize the 7-segment displays
TM_DRIVERS = [tm1637.TM1637(clk=Pin(clk), dio=Pin(dio)) for clk, dio in TM_PINS]
# define reset button input
RESET_BTN_PIN = Pin(RESET_BUTTON_PIN, Pin.IN, Pin.PULL_UP)

# create instance(s) of lcd
lcd = Display(scl_pin=LCD_PIN_SCL,
    sda_pin=LCD_PIN_SDA,
    address=LCD_ADDRESS)

# create instances of led(s)
status = LED(STATUS_LED_PIN)

# Global variables
RANK = []
PREVIOUS_RANK = []
STOP_DISPLAY_UPDATES = False

def check_reset_button():
    global RANK, PREVIOUS_RANK, STOP_DISPLAY_UPDATES
    if RESET_BTN_PIN.value() == 0:
        # clear displays
        segment_display_handler(BLANK_DISPLAY)
        lcd.clear()
        # reset for next race
        RANK = []
        PREVIOUS_RANK = []
        # resume display updates
        STOP_DISPLAY_UPDATES = False
        utime.sleep(0.3)  # Debounce button delay

def segment_display_handler(content):
    for driver in TM_DRIVERS:
        driver.write(content)
    utime.sleep(0.01)

def check_ldr_sensors():
    global RANK
    for i, ldr_pin in enumerate(LDR_SENSORS):
        lane = LDR_PIN_MAP[ldr_pin]['lane']
        if ldr_pin.value() == 1 and (lane) not in RANK:
            RANK.append(lane)
    utime.sleep(0.01)  # Debounce delay

def lcd_race_status(content):
    lines = [
        "FIRST - ",
        "SECOND - ",
        "THIRD - ",
        "FORTH - "
    ]
    output = []
    # build lines for LCD
    for i in range(len(content)):
        output.append(lines[i] + content[i])
    lcd.write(output)

def startup_procedure():
    # Initialize segement displays on first start
    segment_display_handler(BLANK_DISPLAY)
    # Clear LCD display
    lcd.clear()
    # handle wifi connection
    connected = networking.connect_wifi(WIFI_SSID)
    if not connected:
        lcd.write(["","NO WIFI","CONNECTION",""])
        status.on(5)

# run startup
startup_procedure()

# print welcome message
lcd.write(["INIT","COMPLETE","READY TO","RACE"])

# Main loop to check sensors and update display
while True:
    # check sensors
    check_ldr_sensors()
    # if a sensor has registered, start updating display(s)
    if RANK and not STOP_DISPLAY_UPDATES:
        # Skip LCD update if same as the previous cycle
        if RANK != PREVIOUS_RANK:
            segment_display_handler(RANK)
            lcd_race_status(RANK)
            PREVIOUS_RANK = RANK
    # once the last place registers, we can stop updating the
    # display on each cycle until the reset button is pressed
    if len(RANK) == LANE_COUNT:
        STOP_DISPLAY_UPDATES = True
    # check if reset button is pressed
    check_reset_button()
