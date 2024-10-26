
from typing import TypedDict
import requests
import json

class DeviceCodeDict(TypedDict):
    device_code: str
    user_code: str
    verification_uri: str
    expires_in: int
    interval: int
    verification_uri_complete: str

class DeviceCode():
    def __init__(self, domain, client_id, scope, audience):
        self.url = 'https://{_domain}/oauth/device/code'.format(_domain = domain)
        self.headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        self.data = {
            'client_id': client_id,
            'scope': scope,
            'audience': audience
        }
    
    def request(self):
        self.response = requests.post(self.url, headers=self.headers, data=self.data, verify=False)

    def getStatusCode(self):
        return self.response.status_code
    
    def getResponseJSON(self) -> DeviceCodeDict:
        return json.loads(self.response.text)