import requests
import json
import base64
import sys
import os
from dotenv import load_dotenv

if getattr(sys, 'frozen', False):
    BUNDLE_DIR = os.path.dirname(sys.executable)
else:
    BUNDLE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")

def encode_base64(json):
    # Convert the refresh token string to bytes
    refresh_token_bytes = json.encode('utf-8')
    
    # Encode the refresh token bytes using Base64
    encoded_token = base64.b64encode(refresh_token_bytes)
    
    return encoded_token.decode('utf-8')

class AccessToken():
    def __init__(self, domain, client_id, device_code):
        self.url = 'https://{_domain}/oauth/token'.format(_domain = domain)
        self.headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        self.data = {
            'client_id': client_id,
            'grant_type': "urn:ietf:params:oauth:grant-type:device_code",
            'device_code': device_code
        }

    def request(self):
        self.response = requests.post(self.url, headers=self.headers, data=self.data, verify=False)

    def getStatusCode(self):
        return self.response.status_code
    
    def getResponseJSON(self):
        return json.loads(self.response.text)
    
    def storeAtFile(self):
        token = json.loads(self.response.text)
        storeTokenAtFile(token)
        
def storeTokenAtFile(token: dict):
    # token["expires_at"] = time.time() + token["expires_in"] - 60 # Safe margin
    encoded_json = encode_base64(json.dumps(token))
    # Save the encoded refresh token to a file
    file_dir = os.path.dirname(os.path.join(BUNDLE_DIR, "resources", "json.txt"))
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)

    file_path = os.path.join(BUNDLE_DIR, "resources", "json.txt")
    with open(file_path, 'w') as file:
        file.write(encoded_json)