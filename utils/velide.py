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
            mutation AddDeliveryFromIntegration($metadata: MetadataInput!, $address: String, $reference: String) {
                addDeliveryFromIntegration(
                    metadata: $metadata
                    address: $address
                    reference: $reference
                ) {
                    id
                    routeId
                    endedAt
                    expectedEnd
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
                'reference': sale_info["reference"]
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
        return response.json()["data"]["addDeliveryFromIntegration"]
    
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