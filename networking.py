import network
import time

def connect_wifi(ssid, password=None):
    connected = False
    # Initialize the WiFi interface
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    # Connect to the WiFi network
    if password:
        wlan.connect(ssid, password)
    else:
        wlan.connect(ssid)

    # Wait for connection
    max_attempts = 10
    attempts = 0
    while not wlan.isconnected() and attempts < max_attempts:
        print('Connecting to network...')
        time.sleep(1)
        attempts += 1

    # Check if connected
    if wlan.isconnected():
        print('Connected to', ssid)
        print('Network config:', wlan.ifconfig())
        connected = True
    else:
        print('Failed to connect to', ssid)
        connected = False

    return connected