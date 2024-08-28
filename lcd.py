from machine import I2C, Pin
from lcd_i2c import LCD

class Display:
    def __init__(self, scl_pin = 17, sda_pin = 16, address = 0x27, rows = 4, columns = 20):
        # Initialize I2C
        self.i2c = I2C(0, scl=Pin(17), sda=Pin(16), freq=400000)

        # Initialize LCD
        self.lcd = LCD(self.i2c, 0x27, 2, 16)  # Address 0x27, 2 rows, 16 columns
        self.lcd.begin()

        # make constants available
        self.columns = columns
        self.rows = rows

    def clear(self):
        self.lcd.clear()

    def center_text(self, text, width):
        if len(text) < width:
            padding = (width - len(text)) // 2
            return ' ' * padding + text + ' ' * padding
        return text

    def write(self, lines):
        i = 0
        self.lcd.clear()
        for line in lines:
            # if there is display overrun, we'll ignore those lines
            if i < self.rows:
                self.lcd.setCursor(0, i)
                self.lcd.print(self.center_text(line.strip(), self.columns))
                i += 1
