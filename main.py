import csv
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import json

# API request setup
url = "https://www.zillow.com/async-create-search-page-state"

payload = {
    "searchQueryState": {
        "pagination": {"currentPage": 2},
        "isMapVisible": False,
        "mapBounds": {
            "west": -86.50791361914062,
            "east": -85.78006938085937,
            "south": 39.56013167919673,
            "north": 39.999170936785674
        },
        "usersSearchTerm": "Indianapolis, IN",
        "regionSelection": [
            {
                "regionId": 32149,
                "regionType": 6
            }
        ],
        "filterState": {
            "sortSelection": {"value": "globalrelevanceex"},
            "isAllHomes": {"value": True}
        },
        "isListVisible": True
    },
    "wants": {
        "cat1": ["listResults"],
        "cat2": ["total"]
    },
    "requestId": 7,
    "isDebugRequest": False
}

headers = {
    "cookie": "your_cookie_here",
    "accept": "*/*",
    "accept-language": "en-US,en-PK;q=0.9,en;q=0.8",
    "content-type": "application/json",
    "origin": "https://www.zillow.com",
    "priority": "u=1, i",
    "referer": "https://www.zillow.com/indianapolis-in/8_p/?searchQueryState=%7B%22pagination%22%3A%7B%22currentPage%22%3A8%7D%2C%22isMapVisible%22%3Atrue%2C%22mapBounds%22%3A%7B%22west%22%3A-86.50791361914062%2C%22east%22%3A-85.78006938085937%2C%22south%22%3A39.56013167919673%2C%22north%22%3A39.999170936785674%7D%2C%22usersSearchTerm%22%3A%22Indianapolis%2C%20IN%22%2C%22regionSelection%22%3A%5B%7B%22regionId%22%3A32149%2C%22regionType%22%3A6%7D%5D%2C%22filterState%22%3A%7B%22sort%22%3A%7B%22value%22%3A%22globalrelevanceex%22%7D%2C%22ah%22%3A%7B%22value%22%3Atrue%7D%7D%2C%22isListVisible%22%3Atrue%7D",
    "sec-ch-ua": "\"Google Chrome\";v=\"125\", \"Chromium\";v=\"125\", \"Not.A/Brand\";v=\"24\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
}

# API request
response = requests.request("PUT", url, json=payload, headers=headers)

# JSON response ko Python dictionary mein convert karna
data = response.json()

# Debugging: JSON response ko print karna
print(json.dumps(data, indent=4))

filename = "zillow-info.csv"

# ye sari lists hain
detail_urls = []
all_address = []
price = []
imgscr = []
beds = []
baths = []
area = []
brokerName = []
try:
    list_results = data['cat1']['searchResults']['listResults']
    for result in list_results:
        # Debugging: Result ko print karna
        print(result)
        if all(key in result for key in ["detailUrl", "brokerName", "address", "price", "imgSrc", "beds", "baths", "area"]):
            detail_urls.append(result['detailUrl'])
            all_address.append(result['address'])
            price.append(result['price'])
            imgscr.append(result['imgSrc'])
            beds.append(result['beds'])
            baths.append(result['baths'])
            area.append(result['area'])
            brokerName.append(result['brokerName'])
        else:
            missing_keys = [key for key in ["detailUrl", "brokerName", "address", "price", "imgSrc", "beds", "baths", "area"] if key not in result]
            print(f"Missing keys in result: {missing_keys}")
except KeyError as e:
    print(f"Key error: {e}")

print("Detail URLs:")
with open(filename, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Broker Name", "URL", "Address", "Price", "Beds", "Baths", "Area"])
    for url, address, allprice, imgsrc, bed, bath, all_area, all_brokername in zip(detail_urls, all_address, price, imgscr, beds, baths, area, brokerName):
        print(f"Broker Name: {all_brokername} URL: {url}, Address: {address}, Price: {allprice}, Image: {imgsrc}, Beds: {bed}, Baths: {bath}, Area: {all_area}")
        writer.writerow([all_brokername, url, address, allprice, bed, bath, all_area])

# detailUrl values ko CSV file mein save karna
csv_file = "detail_urls.csv"
with open(csv_file, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Detail URL"])
    for url in detail_urls:
        writer.writerow([url])

print(f"Detail URLs have been saved to {csv_file}")

AGENT_PH_NUMBER = []
AGENT_NAME = []

with open('agents.csv', 'a+', newline='') as csvfile:
    writer = csv.writer(csvfile)
    ua = UserAgent()

    for all_urls in detail_urls:
        headers = {'User-Agent': ua.random}
        response = requests.get(all_urls, headers=headers)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            script_tag = soup.find('script', id='__NEXT_DATA__', type='application/json')

            if script_tag:
                json_data = script_tag.string
                data = json.loads(json_data)

                with open('property_data.json', 'w') as json_file:
                    json.dump(data, json_file, indent=4)
                print("JSON data has been saved to property_data.json")

                try:
                    gdp_client_cache = data['props']['pageProps']['componentProps']['gdpClientCache']
                    gdp_client_cache_data = json.loads(gdp_client_cache)

                    for key, value in gdp_client_cache_data.items():
                        print(f"<< Url: {all_urls} >>")

                        agent_phone_number = value['property']['attributionInfo'].get('agentPhoneNumber', "N/A")
                        agent_name = value['property']['attributionInfo'].get('agentName', "N/A")

                        print(f"Agent Phone Number: {agent_phone_number}")
                        print(f"Agent Name: {agent_name}")

                        AGENT_PH_NUMBER.append(agent_phone_number)
                        AGENT_NAME.append(agent_name)

                        writer.writerow([all_urls, agent_phone_number, agent_name])
                except KeyError as e:
                    print(f"Key error: {e}")
                    writer.writerow([all_urls, "N/A", "N/A"])
            else:
                print("Script tag with id '__NEXT_DATA__' not found.")
                writer.writerow([all_urls, "N/A", "N/A"])
        else:
            print(f"Failed to retrieve the page. Status code: {response.status_code}")
            writer.writerow([all_urls, "N/A", "N/A"])

csv_file = "property_details_with_agents.csv"
with open(csv_file, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Detail URL", "Address", "Price", "Beds", "Baths", "Agent Phone Number", "Agent Name"])
    for row in zip(detail_urls, all_address, price, beds, baths, AGENT_PH_NUMBER, AGENT_NAME):
        writer.writerow(row)

print(f"All details have been saved to {csv_file}")

print("Data appended to agents.csv successfully!")
print("----------------------------------------------------------")
