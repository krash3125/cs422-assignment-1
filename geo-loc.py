import requests
import os
import json
import time

path = os.path.join(os.path.dirname(__file__), "data", "listed_iperf3_servers.json")
output_path = os.path.join(
    os.path.dirname(__file__), "data", "servers_with_geo_loc.json"
)


def get_coordinates(ip):
    url = f"http://ip-api.com/json/{ip}?fields=status,country,city,lat,lon"
    response = requests.get(url)

    if response.status_code != 200:
        return None

    data = response.json()

    if "status" in data and data["status"] == "fail":
        return None

    return response.json()


results = []

with open(path, "r", encoding="utf-8") as file:
    data = json.load(file)

    count = 0
    for server in data:
        if count == 45:
            time.sleep(60)
            count = 0

        coordinates = get_coordinates(server["IP/HOST"])
        count += 1
        if coordinates:
            print(f"{server['IP/HOST']} ({coordinates['lat']}, {coordinates['lon']})")
            results.append(
                {**server, "lat": coordinates["lat"], "lon": coordinates["lon"]}
            )
        else:
            print(f"{server['IP/HOST']} (None)")


with open(output_path, "w", encoding="utf-8") as output_file:
    json.dump(results, output_file, indent=4)
