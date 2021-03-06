#!/usr/bin/env python3

# -*- coding: utf-8 -*-

import requests
import json
import sys
import argparse
from easysnmp import Session

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-host","--hostname", help="Hostname", default="localhost")
    parser.add_argument("-v","--version", type=int, choices=[1, 2], help="Version 1 or 2", default=2)
    parser.add_argument("-p","--port", type=int, help="Specify port to use", default=161)
    parser.add_argument("-c","--community", help="Specify Community to use", default="public")
    args = parser.parse_args()
    try:
        ss = Session(hostname=args.hostname, community=args.community, version=args.version)
        firmwareLong = ss.get('1.3.6.1.4.1.12356.101.4.1.1.0').value
        firmware = firmwareLong[1:7]
        firmware = firmware if firmware[5] != "," else firmware[0:5] # chop trailing "," if minor Version <9
    except Exception as e:
        print("ERROR: " + e)
        sys.exit(3)

    url = "http://cve.circl.lu/api/search/fortinet/fortios"
    try:
        response = requests.get(url)
    except requests.exceptions.RequestException as e:
        print("ERROR: " + e)
        sys.exit(3)
        
    r = json.loads(response.text)
    cvelist = []  
    for cve in r:
        try:
            for vulnerableconf in cve["vulnerable_configuration"]:
                if firmware in vulnerableconf:
                    cvelist.append(cve["id"])
        except KeyError:
            print("Key in JSON Response not found!")
            sys.exit(3)
        try:
            for vulnerableconf2_2 in cve["vulnerable_configuration_cpe_2_2"]:
                if firmware in vulnerableconf:
                    cvelist.append(cve["id"])
        except KeyError:
            print("Key in JSON Response not found!")
            sys.exit(3)
    if len(cvelist) != 0:
        print("CRITICAL: Vulnerabilities found for " + firmwareLong, end=" ")
        print(cvelist)
        sys.exit(2)
    else:
        print("OK: No vulnerability found for " + firmwareLong)
        sys.exit(0)

if __name__ == '__main__':
    main()
