""" Create a CSV file of all requested stops and thier IDs
This script downloads all stops for a given rapid-transit route using the
TransitLand API and puts them in a CSV file with stop name, agency stop ID, and
a placeholder value that can eventually represent the LED index the physical
stop LED is connected to.

Stops to download are loading in from the lines_to_download YAML file. In this
file, the key for each line is not used and provided for ease of use/reference
between agency line IDs and TransitLand line IDs. The value for each key in the
YAML file is the TransitLand OneStop ID number, which can be manually found and
inputted by searching the line on the TransitLand website.

Additionally, the TransitLand API key is stored in the overall project config
file (mbta-map-config.yml) in a seperate section.

More information about TransitLand, thier API, and getting an API can be found
at: https://www.transit.land/


Written by:
Carter Harris
Olin College of Engineering
"""
import csv
import yaml
import requests

# The overall project config file is loaded to pull in the Transitland API key
with open("mbta-map-config.yml", "r", encoding="utf-8") as cfgfile:
    config = yaml.safe_load(cfgfile)

# All parameters needed to make a request to the Transitland API are defined,
# including an API base URL, the API key (and saving this in an appropriate
# HTTP header format), and a global timeout for when making the request.
transit_land_key = config["transit_land"]["api_key"]
transit_land_headers = {"apikey": transit_land_key}
TRANSIT_LAND_URL = "https://transit.land/api/v2/rest/"
TRANSIT_LAND_TIMEOUT = 5

# The goal of this script is to output a file that can be manually filled in
# based on the specific wiring of a given map. In the meantime, a placeholder
# value is placed to represent where LED indexes will eventually go.
LED_PLACEHOLDER = 0

# The lines to download stops for are loaded from the outside configuration
# file. The script is structured in this way such that it can reasonably be
# customized (differnt lines/scope of map, potenital a differnt system) without
# having to modify the actual Python script. This file is encoded in YAML format
# so the corresponding library is used to load it.
lines = {}
with open("lines.yml", "r", encoding="utf-8") as linefile:
    lines = yaml.safe_load(linefile)

# An empty list to represent all stops is created.
stop_list = []

# This for loop individually downloads data for each of the lines loaded from
# the configuration file, looping through the created dictionary.
for key, line in lines.items():
    # Construct the Transitland API request URL for the line currently being
    # searched.
    line_request_url = TRANSIT_LAND_URL + "routes/" + line
    # Make the API request to the Transitland API given our constructed URL and
    # previous defined key & parameters.
    line_data = requests.get(
        line_request_url, headers=transit_land_headers, timeout=TRANSIT_LAND_TIMEOUT
    )
    # The Transitland REST API returns JSON data where all useful information
    # is contained under a "routes" subsection, so this data is extracted from
    # the entire collected data.
    line_json = line_data.json()
    route_json = line_json["routes"]

    # Error handling to check if the provided Transitland OneStop ID from the
    # configuration file is actually valid. If an invalid ID is provided, the
    # API will return an empty response and the for loop will throw an index
    # error as there is nothing to parse.
    try:
        for stop in route_json[0]["route_stops"]:
            # For each stop on the provided line, extract the stop and name
            # from the Transitland-provided JSON format
            stop_id = stop["stop"]["stop_id"]
            stop_name = stop["stop"]["stop_name"]

            # Each stop is represneted in the code as a seperate list within
            # stop_list. This structure allows for easy writing to a CSV file
            # later in the code.
            stop_list.append([stop_id, stop_name, LED_PLACEHOLDER])
    except IndexError:
        print(
            f"Error parsing line {key}. Check that the Transitland OneStop ID number is correct."
        )
        print(f"Current OneStop ID: {line}")


# After all stops for all requested lines have been added to stop_list,
# stop_list can be written to a .csv file with each list representing a new
# line. The newline='' parameter is needed to prevent extra newlines from being
# added. This file is saved in the project parent directory.
#
# Error handeling is added in case the file is not writeable (probably because
# it is already open)
try:
    with open("stop_data.csv", "w", newline="", encoding="utf-8") as file:
        write = csv.writer(file)
        write.writerows(stop_list)
        print(f"Sucessfully wrote {len(stop_list)} stations to stop_data.csv!")
except PermissionError:
    print(
        "The current directory is not writeable, or the stop_data.csv"
        + " file has already been created and is open in another program."
        + " Ensure permissions are correct and close the file if open."
    )
    print("\nFile not written.")
