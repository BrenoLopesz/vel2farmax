from datetime import datetime
import requests
import httpx

class Velide():
    def __init__(self, server, access_token):
        self.url = server
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': access_token
        }

    async def getDeliverymen(self):
        query = """
            query {
                deliverymen {
                    id
                    name
                }
            }
        """
        payload = {
            'query': query,
        }

         # Sending the GraphQL mutation request asynchronously
        async with httpx.AsyncClient() as client:
            response = await client.post(self.url, json=payload, headers=self.headers)

         # Checking for errors
        if response.status_code != 200:
            raise Exception(f"GraphQL mutation failed with status code {response.status_code}: {response.text}")
        
        print(response.json())

        # Parsing and returning the JSON response
        return response.json()["data"]["deliverymen"]
    
    async def getDeliveries(self, start_period_unix_seconds, end_period_unix_seconds):
        query = """
            query GetDeliveries($startPeriod: Int, $endPeriod: Int) {
                deliveries(startPeriod: $startPeriod, endPeriod: $endPeriod) {
                    id
                    route {
                        deliverymanId
                        startedAt
                    }
                    location {
                        properties {
                            name
                        }
                    }
                    endedAt
                }
            }
        """
        payload = {
            'query': query,
            'variables': {
                'startPeriod': int(start_period_unix_seconds),
                'endPeriod': int(end_period_unix_seconds)
            }
        }

         # Sending the GraphQL mutation request asynchronously
        async with httpx.AsyncClient() as client:
            response = await client.post(self.url, json=payload, headers=self.headers)

         # Checking for errors
        if response.status_code != 200:
            raise Exception(f"GraphQL mutation failed with status code {response.status_code}: {response.text}")
        
        print(response.json())

        # Parsing and returning the JSON response
        return response.json()["data"]["deliveries"]

    async def addDelivery(self, sale_info):

        # GraphQL mutation with variables
        mutation = """
            mutation AddDeliveryFromIntegration($metadata: MetadataInput!, $address: String, $reference: String, $offset: Int) {
                addDeliveryFromIntegration(
                    metadata: $metadata
                    address: $address
                    reference: $reference
                    offset: $offset
                ) {
                    id
                    routeId
                    endedAt
                    createdAt
                    location {
                        properties {
                            name
                            housenumber
                            street
                        }
                    }
                }
            }
        """

        today_date = datetime.now().date()
        # sale_info["created_at"] is a datetime.time object
        # We have to combine it to today's date
        datetime_combined = datetime.combine(today_date, sale_info["created_at"])

        # Offset should be an integer
        unix_timestamp = int(datetime_combined.timestamp())
        now = int(datetime.now().timestamp()) 
        offset_in_seconds = now - unix_timestamp
        # Offset should be in milliseconds
        offset = offset_in_seconds * 1000

        # GraphQL request payload
        payload = {
            'query': mutation,
            'variables': { 
                'metadata': {
                    'integrationName': "Farmax",
                    'customerName': sale_info["name"]
                    # 'contact': sale_info["contact"] TODO
                 },
                'address': sale_info["address"],
                'reference': sale_info["reference"],
                # To avoid unneccessary offsets, only set it if is bigger than a minute ago
                'offset': offset if offset > 60000 else 0
            }
        }

        timeout = httpx.Timeout(10.0, read=None)

         # Sending the GraphQL mutation request asynchronously
        async with httpx.AsyncClient() as client:
            response = await client.post(self.url, json=payload, headers=self.headers, timeout=timeout)

         # Checking for errors
        if response.status_code != 200:
            raise Exception(f"GraphQL mutation failed with status code {response.status_code}: {response.text}")
        
        try:
            response_json = response.json()
        except: 
            raise Exception(f"Could not parse response as JSON.", response)
        
        print(response_json)

        if response_json is None or "data" not in response_json or "addDeliveryFromIntegration" not in response_json["data"]:
            raise Exception(f"Unexpected response structure: {response_json}")

        # Parsing and returning the JSON response
        return response_json["data"]["addDeliveryFromIntegration"]
    
    async def deleteDelivery(self, id):

        # GraphQL mutation with variables
        mutation = """
            mutation DeleteDelivery($deliveryId: String!) {
                deleteDelivery(
                    deliveryId: $deliveryId
                )
            }
        """

        # GraphQL request payload
        payload = {
            'query': mutation,
            'variables': { 
                'deliveryId': id,
            }
        }

        timeout = httpx.Timeout(10.0, read=None)

         # Sending the GraphQL mutation request asynchronously
        async with httpx.AsyncClient() as client:
            response = await client.post(self.url, json=payload, headers=self.headers, timeout=timeout)

         # Checking for errors
        if response.status_code != 200:
            raise Exception(f"GraphQL mutation failed with status code {response.status_code}: {response.text}")
        
        print(response.json())

        # Parsing and returning the JSON response
        return response.json()["data"]["deleteDelivery"]