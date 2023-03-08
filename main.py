import yaml
import json
import requests
import socket

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


# Declare lines to monitor:
# All 3-digit lines that begin with 7 are the Silver Line routes
with open("lines.yml", "r", encoding="utf-8") as linefile:
    lines = list(yaml.safe_load(linefile).keys())
    for index, line in enumerate(lines):
        lines[index] = str(line)
        
# Load an outside 


while True:
    mbta_api_response = requests.get(
        mbta_url, headers=mbta_headers, timeout=MBTA_TIMEOUT
    )
    response_json = mbta_api_response.json()

    for item in response_json["data"]:

        if item["relationships"]["route"]["data"]["id"] not in lines:
            continue



        print("Route:" + item["relationships"]["route"]["data"]["id"])
        print("Stop ID:" + item["relationships"]["stop"]["data"]["id"] + "\n")
