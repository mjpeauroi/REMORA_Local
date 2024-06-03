import requests
import os
import re
from data_handling import json_to_csv, save_img_entry, save_txt_entry

# Change the working directory to the script's directory
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# define the tag that indicates it's part of txt data
txt_tag = "<T>"
# img data will be stored and converted separately during for loop in main function


# Function to decode hex to ASCII string
def decode_hex_to_ascii(hex_string):
    byte_value = bytes.fromhex(hex_string)
    try:
        return byte_value.decode('utf-8')
    except UnicodeDecodeError as e:
        # Log the error with the specific problematic byte and its position
        print(f"Error decoding byte: {byte_value[e.start:e.end]} at position {e.start}")
        # Continue with replacing or ignoring the problematic part
        return byte_value.decode('utf-8', errors='replace')  # or 'ignore'


def main():
     # Prompt user for inputs
    spotterId = input("Please enter Spotter ID: ")
    startDate = input("Please enter start date (YYYY-MM-DD): ")
    endDate = input("Please enter end date (YYYY-MM-DD): ")
    token = input("Please enter Spotter token: ")

    # Specify Sofar API URL
    url = f"https://api.sofarocean.com/api/sensor-data?spotterId={spotterId}&startDate={startDate}&endDate={endDate}&token={token}"
    # Specify filepaths
    startDate_only = startDate[:10]
    endDate_only = endDate[:10]
    save_directory = f"{startDate_only}_{endDate_only}/"
    csv_path = f"{save_directory}spotter_data.csv"
    txt_path = f"{save_directory}spotter_message.txt"
    img_path = f"{save_directory}imgs/"

    # Attempt to "connect" to url and fetch data
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        return
    except requests.exceptions.ConnectionError as conn_err:
        print(f"Connection error occurred: {conn_err}")
        return
    except requests.exceptions.Timeout as timeout_err:
        print(f"Timeout error occurred: {timeout_err}")
        return
    except requests.exceptions.RequestException as req_err:
        print(f"An error occurred: {req_err}")
        return

    # Pull data from url as json file
    try:
        data = response.json()
    except ValueError as json_err:
        print(f"Error parsing JSON: {json_err}")
        return

    print("Data fetched successfully.")


    # Make directory to store both img and txt data in
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)
    json_to_csv(csv_path, data)

    # Create directory to hold imgs in
    img_directory = os.path.join(save_directory, "imgs")
    if not os.path.exists(img_directory):
        os.makedirs(img_directory)

    # Ensure txt file directory exists
    if not os.path.exists(os.path.dirname(txt_path)):
        os.makedirs(os.path.dirname(txt_path))

    # Variables for img data:
    # "collecting_image_data" indicates whether img data is being dealt with
    # "image_data" holds all the img data 
    # "image_index" specifies the img id

    collecting_image_data = False
    image_data = []
    image_index = None


    # Loop for parsing through all data
    for entry in data['data']:

        # Convert hex data to ASCII and get parameters latitude, longitude, and timestamp
        decoded_value = decode_hex_to_ascii(entry['value'])
        latitude = entry['latitude']
        longitude = entry['longitude']
        timestamp = entry['timestamp']

        # Conditionals on img data and txt data
        if decoded_value.startswith('<START IMG'): # checks if data entry starts with <START IMG>
            collecting_image_data = True # will now run conditionals for img data only
            image_data = [] 
            image_index = re.search(r'<START IMG (\d+)>', decoded_value).group(1)
        elif decoded_value.startswith('<END IMG') and collecting_image_data: # turns off specific conditionals for img data
            save_img_entry(image_data, image_index, img_directory) # converts collected data to image and saves it 
            collecting_image_data = False
            image_data = [] # clears data for possible future images with new data
        elif collecting_image_data:
            match = re.search(r'<I(\d+)>', decoded_value) 
            if match: # finds data with <Ixx> tag to store in image_data
                tag_number = int(match.group(1))
                content = decoded_value[decoded_value.find('>')+1:]  # Extract data after the tag
                image_data.append((tag_number, content))
        elif decoded_value.startswith(txt_tag): # runs text conversion if data entry has text tag
            save_txt_entry(txt_path, latitude, longitude, timestamp, decoded_value)

if __name__ == "__main__":
    main()
