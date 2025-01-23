import network
import time

def connect_wifi(ssid, password):
    connected = False

    # Initialize the network interface
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    # disconnect if already connected
    if wlan.isconnected():
        wlan.disconnect()

    # Connect to the Wi-Fi network
    wlan.connect(ssid, password)

    # Wait for connection
    max_attempts = 10
    attempts = 0
    while not wlan.isconnected() and attempts < max_attempts:
        print('Connecting to network...')
        time.sleep(2)
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