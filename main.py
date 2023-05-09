import time
import yaml
import json
import requests
import socket
import pandas as pd

# CircuitPython Imports
import board
import busio
import digitalio

import adafruit_tlc5947

LED_BRIGHTNESS = 2048

# load configuration YAML file
# Loads MBTA API key & Gotify configuration
with open("mbta-map-config.yml", "r") as ymlfile:
    config = yaml.safe_load(ymlfile)

# Setup nessesary information for API requests
# This is specifically set to use vehicles API
mbta_api_key = config["mbta"]["api_key"]
mbta_url = "https://api-v3.mbta.com/vehicles"
mbta_headers = {"X-API-Key": mbta_api_key}
MBTA_TIMEOUT = 5

# Setup Gotify notification system API information
#
gotify_enabled = config["gotify"]["enabled"]
if gotify_enabled:
    gotify_url = config["gotify"]["url"]
    gotify_key = config["gotify"]["token"]


# Declare the LED controller boards
SCK = board.SCK
MOSI = board.MOSI
LATCH = digitalio.DigitalInOut(board.D5)
spi = busio.SPI(clock=SCK, MOSI=MOSI)
tlc5947 = adafruit_tlc5947.TLC5947(spi, LATCH, auto_write=False, num_drivers=7)

# Declare lines to monitor:
with open("lines.yml", "r", encoding="utf-8") as linefile:
    lines = list(yaml.safe_load(linefile).keys())
    for index, line in enumerate(lines):
        lines[index] = str(line)
        
# Load an outside
with open("stop_data.csv", 'r', encoding="utf-8") as stopfile:
    stop_to_led = pd.read_csv(stopfile)


while True:
    # Get API response from MBTA
    mbta_api_response = requests.get(
        mbta_url, headers=mbta_headers, timeout=MBTA_TIMEOUT
    )
    # Convert to JSON for easy indexing
    response_json = mbta_api_response.json()

    # Loop through each vehicle returned from the API
    for item in response_json["data"]:

        # Load Route and Stop_id - only data from response that is used
        route = item["relationships"]["route"]["data"]["id"]
        stop_id = item["relationships"]["stop"]["data"]["id"]

        # if route is not one of the ones being tracked that we have stop
        # data for, then skip to the next vehicle (this mainly skips bus lines
        # that are not being tracked)
        if route not in lines:
            continue
        
        # convert the stop_id into a led_id, and then turn that LED on
        row = stop_to_led.loc[stop_to_led['stop_id'] == "70061"]
        led_id = row.loc[0, "led_id"]
        if led_id != 0 and led_id != -1:
            tlc5947[led_id] = LED_BRIGHTNESS
    
    # Write the current set of LEDs to be on
    tlc5947.write()

    # Wait 10 seconds before the next update
    time.sleep(10)

    # Turn all LEDs back off
    for led_id in stop_to_led["led_id"].tolist():
        if led_id != 0 and led_id != -1:
            tlc5947[led_id] = 0

