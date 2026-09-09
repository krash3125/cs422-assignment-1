import json
import os
import subprocess
import time
import socket

path = os.path.join(os.path.dirname(__file__), 'listed_iperf3_servers.json')
output_path = os.path.join(os.path.dirname(__file__), 'iperf3_results.json')


with open(path, 'r', encoding='utf-8') as file:
    data = json.load(file)
    chart_data = {}
    
    print("PT2")
    
    for i, server in enumerate(data[:5]):
       print("----------------------------------------")
       print(f"Testing: {server['SITE']}, {server['CONTINENT']}")
       try:
        result = subprocess.run(['traceroute', '-w', '1', server["IP/HOST"]], capture_output=True, text=True, check=True)
        filtered = [line for line in result.stdout.splitlines() if "*" not in line.strip()]
        
        chart_data[server['IP/HOST']] = None
        current_hop = None
    
        filtered_results = []
        
        for line in filtered:
            split_line = line.split()
            
            if len(split_line) <= 2:
                continue
            
            if split_line[0].isdigit():
                current_hop = split_line[0]
                ip = split_line[1]
            else:
                ip = split_line[0]

            total_latency = 0
            num_pings = 0

            for j, part in enumerate(split_line):
                if part == "ms" and j > 0:
                    total_latency += float(split_line[j - 1])
                    num_pings += 1

            if num_pings > 0:
                avg_latency = round(total_latency / num_pings, 3)
                filtered_results.append((current_hop, ip, avg_latency))
        
        chart_line = []
        for j, line in enumerate(filtered_results):
            print("Hop " + line[0] + " IP: " + line[1] + " Latency: " + str(line[2]) + " ms")
            
            stacked_latency = filtered_results[j][2] if (j == 0) else (filtered_results[j][2] - filtered_results[j-1][2])
            chart_line.append((line[0], line[1], stacked_latency))
        
        chart_data[server['IP/HOST']] = chart_line
        print(chart_data)
       except subprocess.CalledProcessError as e:
        print(f"Error {server['SITE']}, {server['CONTINENT']}: {e}")
        continue
        

    with open(output_path, 'w', encoding='utf-8') as output_file:
        json.dump(chart_data, output_file, indent=4)      
    