import matplotlib.pyplot as plt
import json
import os
import geocoder
from geopy.distance import geodesic
import numpy as np

ping_results = os.path.join(os.path.dirname(__file__), "data", "iperf3_results.json")
coord_results = os.path.join(
    os.path.dirname(__file__), "data", "servers_with_geo_loc.json"
)
traceroute_results = os.path.join(
    os.path.dirname(__file__), "data", "traceroute_results.json"
)

data = []

with open(ping_results, "r", encoding="utf-8") as file:
    ping_data = json.load(file)
    data = ping_data

with open(coord_results, "r", encoding="utf-8") as file:
    coord_data = json.load(file)
    final_data = []
    for coord in coord_data:
        for ping in ping_data:
            if ping["IP/HOST"] == coord["IP/HOST"]:
                final_data.append({**ping, **coord})
    data = final_data

full_data = []

myloc = geocoder.ip("me")
my_coordinates = (myloc.latlng[0], myloc.latlng[1])

for x in data:
    server_coordinates = (x["lat"], x["lon"])
    distance = geodesic(my_coordinates, server_coordinates).miles
    full_data.append({**x, "distance": distance})


distances = [item["distance"] for item in full_data]
min_rtt = [item["min_rtt"] for item in full_data]
mean_rtt = [item["mean_rtt"] for item in full_data]
max_rtt = [item["max_rtt"] for item in full_data]


plt.figure()
plt.scatter(distances, min_rtt, edgecolors="white", linewidths=0.5, alpha=0.8)
plt.xlabel("Distance (miles)")
plt.ylabel("Min RTT (ms)")
plt.title("Min RTT vs Distance")
plt.savefig("./plots/min_rtt_vs_distance.png")

plt.figure()
plt.scatter(distances, mean_rtt, edgecolors="white", linewidths=0.5, alpha=0.8)
plt.xlabel("Distance (miles)")
plt.ylabel("Mean RTT (ms)")
plt.title("Mean RTT vs Distance")
plt.savefig("./plots/mean_rtt_vs_distance.png")

plt.figure()
plt.scatter(distances, max_rtt, edgecolors="white", linewidths=0.5, alpha=0.8)
plt.xlabel("Distance (miles)")
plt.ylabel("Max RTT (ms)")
plt.title("Max RTT vs Distance")
plt.savefig("./plots/max_rtt_vs_distance.png")

traceroute_data = {}

with open(traceroute_results, "r", encoding="utf-8") as file:
    traceroute_data = json.load(file)


hops = []
rtt = []

stacked_rtt = {}

for k, v in traceroute_data.items():
    tmp = []
    hops.append(int(v[-1][0]))
    rtt.append(v[-1][3])
    for x in v:
        tmp.append(0 if x[2] < 0 else x[2])

    stacked_rtt[k] = tmp

plt.figure()
plt.scatter(hops, rtt, edgecolors="white", linewidths=0.5, alpha=0.8)

for ip, hop, r in zip(traceroute_data.keys(), hops, rtt):
    plt.annotate(ip, (hop, r), xytext=(5, 5), textcoords="offset points")

plt.xlabel("Hop Count")
plt.ylabel("Mean RTT (ms)")
plt.title("Hop Count vs Mean RTT")
plt.savefig("./plots/hop_count_vs_rtt.png")


fig, ax = plt.subplots()

for ip, rtts in stacked_rtt.items():
    bottom = 0

    for rtt in rtts:
        ax.bar(ip, rtt, width=0.5, bottom=bottom)
        bottom += rtt

ax.set_xlabel("Destination IP")
ax.set_ylabel("RTT (ms)")

plt.xticks(rotation=30, ha="right", fontsize=8)
plt.tight_layout()
plt.savefig("./plots/stacked_bar_hops_rtt.png")
