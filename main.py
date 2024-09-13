import networking
from machine import Pin, SoftI2C
from pico_i2c_lcd import I2cLcd
from time import sleep

# LCD I2C address
LCD_ADDR = 0x27
# rows/columns
LCD_ROWS = 4
LCD_COLS = 20

# map out each lane to ldr sensor, add more lanes/sensors here
LDR_PIN_MAP = {
    2: {"lane": 1},
    3: {"lane": 2},
    4: {"lane": 3},
    5: {"lane": 4},
}

# add more places here if more than 4 lanes/places
PLACES = [
    "FIRST",
    "SECOND",
    "THIRD",
    "FORTH",
]

# Constants
RESET_BTN_PIN = Pin(15, Pin.IN, Pin.PULL_UP)
LDR_PINS = list(LDR_PIN_MAP.keys())
LANE_COUNT = len(LDR_PINS)
LDR_SENSORS = [Pin(pin, Pin.IN) for pin in LDR_PINS]
CLOCK_PIN = Pin(6, Pin.OUT)
LCD_SDA = Pin(0)
LCD_SCL = Pin(1)

# Global race variables
RANK = []
STOP_DISPLAY_UPDATES = False

# Initialize I2C and LCD objects
i2c = SoftI2C(sda=LCD_SDA, scl=LCD_SCL, freq=400000)
lcd = I2cLcd(i2c, LCD_ADDR, LCD_ROWS, LCD_COLS)

def reset():
    global RANK, STOP_DISPLAY_UPDATES
    # Clear LCD for next race
    lcd.clear()
    # Reset for next race
    RANK = []
    # Resume display updates
    STOP_DISPLAY_UPDATES = False
    lcd_writer(["READY","TO","RACE",""])
    sleep(1)

def check_reset_button(force = False):
    if RESET_BTN_PIN.value() == 0:
        reset()

def rank_handler(n):
    try:
        return str(RANK[n])
    except IndexError:
        return ""

def lcd_writer(lines):
    i = 0
    for line in lines:
        lcd.move_to(0, i)
        lcd.putstr(line)
        i += 1

def update_lcd_rank(rank, lane):
    lcd.move_to(0, rank)
    lcd.putstr(f"{ PLACES[rank] }: { lane }")

def check_ldr_sensors():
    global RANK
    for i, ldr_pin in enumerate(LDR_SENSORS):
        lane = f"LANE {LDR_PIN_MAP[LDR_PINS[i]]['lane']}"
        # only append lanes that have not previously ranked
        if ldr_pin.value() == 1 and lane not in RANK:
            RANK.append(lane)
            update_lcd_rank(len(RANK) - 1, lane)
    sleep(0.01)  # Sensor Debounce

try:
    # Welcome msg
    lcd_writer(["Welcome to","PyWood Endgate","Starting","Derby Race!"])
    sleep(2)
    lcd.clear()

    # Main loop to check sensors and update display
    while True:
        # Check sensors
        check_ldr_sensors()

        # Once the last place registers, we can stop updating the
        # display on each cycle until the reset button is pressed
        if len(RANK) == LANE_COUNT:
            STOP_DISPLAY_UPDATES = True

        # Check if reset button is pressed
        check_reset_button()

except KeyboardInterrupt:
    # Turn off the display
    print("Shutting down...")
    lcd.backlight_off()
    lcd.display_off()
