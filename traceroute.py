import json
import os
import subprocess
import time
import socket
import random

path = os.path.join(os.path.dirname(__file__), 'listed_iperf3_servers.json')
output_path = os.path.join(os.path.dirname(__file__), 'iperf3_results.json')


with open(path, 'r', encoding='utf-8') as file:
    data = json.load(file)
    rand = random.sample(data, 5)
    chart_data = {}
    
    print("PT2")
    
    for i, server in enumerate(rand):
       print("----------------------------------------")
       print(f"Testing: {server['SITE']}, {server['CONTINENT']}")
       try:
        result = subprocess.run(['traceroute', '-w', '1', '-n', server["IP/HOST"]], capture_output=True, text=True, check=True)
        filtered = result.stdout.splitlines()
        print(filtered)
        chart_data[server['IP/HOST']] = None
        current_hop = None
    
        filtered_results = []
        current_latencies = []
        current_ip = None
        
        for line in filtered:
            split_line = line.split()
            
            if len(split_line) <= 2:
                continue
            
            if split_line[0].isdigit():
                if current_hop == split_line[0]:
                    pass
                else:
                    if current_hop is not None and current_latencies:
                        avg_latency = round(
                            sum(current_latencies) / len(current_latencies), 3
                        )
                        filtered_results.append(
                            (current_hop, current_ip, avg_latency)
                        )

                    current_hop = split_line[0]
                    current_ip = split_line[1]
                    current_latencies = []


            for j, part in enumerate(split_line):
                if part == "ms" and j > 0:
                    current_latencies.append(float(split_line[j - 1]))

        if current_hop is not None and current_latencies:
            avg_latency = round(
                sum(current_latencies) / len(current_latencies), 3
            )
            filtered_results.append(
                (current_hop, current_ip, avg_latency)
            )
        
        chart_line = []
        
        for j, line in enumerate(filtered_results):
            print("Hop " + line[0] + " IP: " + line[1] + " Latency: " + str(line[2]) + " ms")
            
            stacked_latency = filtered_results[j][2] if (j == 0) else (filtered_results[j][2] - filtered_results[j-1][2])
            chart_line.append((line[0], line[1], round(stacked_latency, 3), line[2]))
        
        chart_data[server['IP/HOST']] = chart_line
        
        print(chart_data)
       except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"Error {server['SITE']}, {server['CONTINENT']}: {e}")
        continue
        

    with open(output_path, 'w', encoding='utf-8') as output_file:
        json.dump(chart_data, output_file, indent=4)      
    