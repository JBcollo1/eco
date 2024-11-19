from flask import Flask, request, send_from_directory
import	os
from flask_restful import Resource, reqparse
from flask_sqlalchemy import SQLAlchemy

import subprocess

class StartMalware(Resource):
    def get(self):
        device_id = request.args.get('device_id')
        if not device_id:
            return "Device ID is missing.", 404

        # Simulate malware installation and scanning
        simulate_malware_installation(device_id)

        # Simulate vulnerability exploitation and data theft
        exploit_result = exploit_vulnerabilities(device_id)
        if exploit_result:
            steal_sensitive_data(device_id)
            status = "Compromised"
        else:
            status = "Scan Completed"

        # Update device status in the database
        update_device_status(device_id, status)
        return f"Malware process finished for Device {device_id}. Status: {status}"

# Endpoint to download stolen data
class DownloadData(Resource):
    def get(self):
        data_files = os.listdir('data/')
        if not data_files:
            return "No data available for download.", 404
        return send_file(os.path.join('data/', data_files[0]), as_attachment=True)

# Add the resources to the API


# Simulated functions
def simulate_malware_installation(device_id):
    print(f"Installing malware on Device {device_id}...")
    # Simulate malware installation process
    installation_successful = True
    if installation_successful:
        print("Malware installed. Initiating scan...")
        # Simulate vulnerability scan
        vulnerabilities = ["Outdated Software", "Weak Encryption"]
        return vulnerabilities
    else:
        return "Malware installation failed."

def exploit_vulnerabilities(device_id):
    print(f"Exploiting vulnerabilities on Device {device_id}...")
    # Simulate exploitation process
    exploit_successful = True
    return exploit_successful

def steal_sensitive_data(device_id):
    print(f"Stealing data from Device {device_id}...")
    # Simulate data theft
    stolen_data = ["Login Credentials", "Personal Documents"]
    save_data_to_disk(stolen_data, device_id)
    return "Data theft successful."

# Simulated database functions
def update_device_status(device_id, status):
    # Update device status in the database
    print(f"Updating status for Device {device_id} to {status}.")

def save_data_to_disk(data, device_id):
    # Save stolen data to disk
    data_file = f"data_from_{device_id}.txt"
    with open(data_file, 'w') as file:
        for item in data:
            file.write(item + '\n')
