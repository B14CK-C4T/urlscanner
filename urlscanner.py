#!/usr/bin/env/python3
#######################################################################################
 #* urlscanner Tool
 #* copyright (c) 2025 B1ACK_C4T
 #* this program is free software: you can redistribute it and/or modify
 #* it under the terms of the GNU General Public License as published by
 #* the Free Software Foundation, either version 3 of the License, or
 #* (at your option) any later version.
 #* 
 #* this program is distributed in the hope that it will be useful,
 #* but WITHOUT ANY WARRANTY; without even the implied warranty of
 #* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 #* GNU General Public License for more details.
 #* 
 #* You should have received a copy of the GNU General Public License
 #* along with this program. If not, see <http://www.gnu.org/licenses/>.
#######################################################################################

import requests
import json
import yaml
import time

def load_config(path):
    try:
        with open(path, "r") as file:
            config = yaml.safe_load(file)
        return config
    except FileNotFoundError:
        print("[!] Error: config file not found")
        return None
    except yaml.YAMLError as e:
        print(f"[!] Error: reading yaml file: {e}")
        return None

def get_url():
    search = input("[*] Search for domains, IPs, filenames, hashes, ASNs: ")
    return search
    
def main():
    config = load_config("config.yaml")
    if not config:
        exit(1)

    api_key = config.get("apikey")
    api_url = "https://urlscan.io/api/v1/scan/"
    if not api_key:
        print("[!] Error: missing API KEY in config file ")
    
    headers = {'API-Key': api_key,'Content-Type':'application/json'}
    
    url = get_url()
    data = {"url": url, "visibility": "public"}
    
    try:
        response = requests.post(api_url, data=json.dumps(data), headers=headers)
        response.raise_for_status()
        print("[*] status code:", response.status_code)
        
        response_data = response.json()
        
        #extract url contains uuid
        uuid = response_data.get("uuid")

        if not uuid:
            print("[!] Error uuid not found in response")
            exit(1)
        
        result_api_url = f"https://urlscan.io/api/v1/result/{uuid}/"

        max_attempts = 10
        delay = 5

        for attempt in range(max_attempts):
            print(f"[!] checking result (attempt {attempt+1}/{max_attempts})...")
        
            response2 = requests.get(result_api_url, headers=headers)
            
            if response2.status_code == 200:
                print("[*] response:\n",json.dumps(response2.json(), indent=4))
                break
            else:
                print("[!] result not ready yet. retrying...")
                time.sleep(delay)
        else:
            print("[!] Error: maximum retry attempts reached. task may still be processing.")
        
    except requests.exceptions.ConnectionError:
        print("[!] Error: unable to connect to the api")
    except requests.exceptions.HTTPError as e:
        print(f"[!] HTTP Error: {e.response.status_code} - {e.response.text}")
    except requests.exceptions.RequestExceptions as e:
        print(f"[!] request Error {e}")


if __name__ == "__main__":
    main()
