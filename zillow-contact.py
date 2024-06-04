import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import json

# Create a UserAgent object to generate a random user agent
ua = UserAgent()
headers = {'User-Agent': ua.random}

# URL of the Zillow page
url = "https://www.zillow.com/homedetails/2737-N-Boehning-St-Indianapolis-IN-46219/1229518_zpid/"

# Send a GET request to the URL with the fake user agent
response = requests.get(url, headers=headers)

# Check if the request was successful
if response.status_code == 200:
    # Parse the page content with BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the script tag with id "__NEXT_DATA__"
    script_tag = soup.find('script', id='__NEXT_DATA__', type='application/json')

    if script_tag:
        # Extract the JSON content from the script tag
        json_data = script_tag.string

        # Load JSON data into a Python dictionary
        data = json.loads(json_data)

        # Save the JSON data to a file
        with open('property_data.json', 'w') as json_file:
            json.dump(data, json_file, indent=4)

        print("JSON data has been saved to property_data.json")

        # Extract the agentPhoneNumber dynamically
        try:
            gdp_client_cache = data['props']['pageProps']['componentProps']['gdpClientCache']
            gdp_client_cache_data = json.loads(gdp_client_cache)

            # Iterate through keys to find the relevant one
            for key, value in gdp_client_cache_data.items():
                if 'agentPhoneNumber' in value.get('property', {}).get('attributionInfo', {}):
                    agent_phone_number = value['property']['attributionInfo']['agentPhoneNumber']
                    print(f"Agent Phone Number: {agent_phone_number}")
                    break
            else:
                print("Agent phone number not found in JSON data.")
        except KeyError as e:
            print(f"Key error: {e}")
    else:
        print("Script tag with id '__NEXT_DATA__' not found.")
else:
    print(f"Failed to retrieve the page. Status code: {response.status_code}")


