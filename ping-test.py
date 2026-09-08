import json
import os
import subprocess
import time
import socket

path = os.path.join(os.path.dirname(__file__), 'listed_iperf3_servers.json')
output_path = os.path.join(os.path.dirname(__file__), 'iperf3_results.json')

final_results = []

def parse_ping(text):
    data = text.split(" = ")[1][:-3]
    values = data.split("/")
    return {
        'min_rtt': float(values[0]),
        'mean_rtt': float(values[1]),
        'max_rtt': float(values[2]),
    }
    
def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    local_ip = s.getsockname()[0]
    s.close()
    return local_ip


local_ip = get_local_ip()
result = subprocess.run(
    ['ping', '-c', '15', local_ip],
    capture_output=True,
    text=True
)
result_data = parse_ping(result.stdout)

local_test_data = {
    'SITE': 'Local Test',
    'CONTINENT': 'Local',
    'IP/HOST': local_ip,
    'PORT': "",
    **result_data
}

final_results.append(local_test_data)


with open(path, 'r', encoding='utf-8') as file:
    data = json.load(file)
    
    for server in data:
      print("----------------------------------------")
      print(f"Testing: {server['SITE']}, {server['CONTINENT']}")
      
      try:
        result = subprocess.run(['ping', '-c', "15", server["IP/HOST"]], capture_output=True, text=True)
        json_data = parse_ping(result.stdout)

        result_data = { **server, **json_data }
        final_results.append(result_data)
        
        print(f"Results: {result_data['max_rtt']}, {result_data['min_rtt']}, {result_data['mean_rtt']}")
        time.sleep(1)
      except subprocess.CalledProcessError as e:
        print(f"Error {server['SITE']}, {server['CONTINENT']}: {e}")
        continue
      

with open(output_path, 'w', encoding='utf-8') as output_file:
    json.dump(final_results, output_file, indent=4)      
    