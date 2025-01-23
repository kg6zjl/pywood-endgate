import networking
from machine import Pin, SoftI2C
from pico_i2c_lcd import I2cLcd
from time import sleep
import uasyncio as asyncio
import urequests as requests
import json

# LCD I2C address
LCD_ADDR = 0x27
# rows/columns
LCD_ROWS = 4
LCD_COLS = 20

# Path to config file
CONFIG_PATH = 'config.json'

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
RESULTS = {}
STOP_DISPLAY_UPDATES = False

class MockLCD:
    def __init__(self):
        pass

    def move_to(self, x, y):
        pass

    def putstr(self, s):
        print(f"{s} \n", end='')

    def clear(self):
        pass

    def home(self):
        pass

    def backlight_off(self):
        pass
    
    def display_off(self):
        pass

# Initialize I2C and LCD objects
try:
    i2c = SoftI2C(sda=LCD_SDA, scl=LCD_SCL, freq=400000)
    lcd = I2cLcd(i2c, LCD_ADDR, LCD_ROWS, LCD_COLS)
except:
    print("Running without LCD")
    lcd = MockLCD()
    sleep(1)
    lcd.clear()

def read_config(file_path):
    try:
        with open(file_path, 'r') as file:
            config = json.load(file)
        return config
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False

def reset():
    global RANK, STOP_DISPLAY_UPDATES, RESULTS
    # Clear LCD for next race
    lcd.clear()
    # Reset for next race
    RANK = []
    RESULTS = {}
    # Resume display updates
    STOP_DISPLAY_UPDATES = False
    lcd_writer(["READY","TO","RACE",""])
    sleep(1)

def check_reset_button():
    if RESET_BTN_PIN.value() == 0:
        reset()

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
    global RANK, RESULTS
    for i, ldr_pin in enumerate(LDR_SENSORS):
        lane = f"LANE {LDR_PIN_MAP[LDR_PINS[i]]['lane']}"
        # only append lanes that have not previously ranked
        if ldr_pin.value() == 1 and lane not in RANK:
            RANK.append(lane)
            update_lcd_rank(len(RANK) - 1, lane)
            RESULTS[len(RANK) - 1] = LDR_PIN_MAP[LDR_PINS[i]]['lane']
    sleep(0.005)  # Sensor Debounce

async def send_results(SERVER, PORT):
    global RESULTS
    url = f"https://{ SERVER }:{ PORT }/api/v1/results"
    while True:
        if RANK:
            try:
                payload = {RESULTS}
                headers = {'Content-Type': 'application/json'}
                response = requests.post(url, json=payload, headers=headers)
                if response.status_code == 200:
                    print("Data sent successfully")
                else:
                    print("Failed to send data")
            except Exception as e:
                print(f"Error sending data: {e}")
        await asyncio.sleep(0.1)

def send_reset(SERVER, PORT):
    global RANK
    url = f"https://{ SERVER }:{ PORT }/api/v1/reset"
    try:
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, headers=headers)
        if response.status_code == 200:
            print("Reset sent successfully")
        else:
            print("Failed to send reset")
    except Exception as e:
        print(f"Error sending reset: {e}")

async def main():
    global STOP_DISPLAY_UPDATES, RANK, LANE_COUNT, SERVER

    # Start the data sending task
    asyncio.create_task(send_results(SERVER, PORT))
    
    try:
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
            await asyncio.sleep(0.01)  # Sensor Debounce
    except KeyboardInterrupt:
        # Turn off the display
        print("Shutting down...")
        lcd.backlight_off()
        lcd.display_off()

try:
    config = read_config(CONFIG_PATH)
    if config:
        network_config = config.get('networking')
        WIFI_SSID = network_config.get('ssid')
        WIFI_PASSWORD = network_config.get('password')
        SERVER = network_config.get('apiserver')
        PORT = network_config.get('port')
    else:
        lcd_writer(["","Failed to","read config",""])
    if network_config.get('enabled'):
        try:
            networking.connect_wifi(WIFI_SSID, WIFI_PASSWORD)
            lcd_writer(["","Wifi Connected:",WIFI_SSID,""])
        except:
            lcd_writer(["Failed to","connect to",WIFI_SSID,""])
    
    # Welcome msg
    lcd_writer(["Welcome to","PyWood Endgate","Starting","Derby Race!"])
    sleep(2)
    lcd.clear()

    # start our async main loop
    asyncio.run(main())

except KeyboardInterrupt:
    # Turn off the display
    print("Shutting down...")
    lcd.backlight_off()
    lcd.display_off()
