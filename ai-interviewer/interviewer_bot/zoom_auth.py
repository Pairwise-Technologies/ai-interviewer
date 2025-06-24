import requests
import os
import base64

from dotenv import load_dotenv

# load .env file 
load_dotenv()

# get creds from .env variables
ACCOUNT_ID = os.environ.get("REST_ACCOUNT_ID")
CLIENT_ID = os.environ.get("REST_CLIENT_ID")
CLIENT_SECRET = os.environ.get("REST_CLIENT_SECRET")

# Zoom OAuth token URL
TOKEN_URL = "https://zoom.us/oauth/token"
# Zoom Zoom Access Token url
ZAK_URL = "https://api.zoom.us/v2/users/me/token?type=zak"

access_token = None
def get_access_token() -> str:
    '''
    
    Function to obtain a S2S OAuth access token from Zoom.
    
    '''
    global access_token
    if access_token != None:
        return access_token
    
    try:
        # Prepare credentials for Basic Auth
        message = f"{CLIENT_ID}:{CLIENT_SECRET}"
        message_bytes = message.encode('ascii')
        base64_bytes = base64.b64encode(message_bytes)
        base64_message = base64_bytes.decode('ascii')

        headers = {
            'Authorization': f'Basic {base64_message}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        payload = {
            'grant_type': 'account_credentials',
            'account_id': ACCOUNT_ID
        }

        print("Requesting Access Token...")
        response = requests.post(TOKEN_URL, headers=headers, data=payload, timeout=10)
        response.raise_for_status()  # Raise HTTPError for bad responses (4XX or 5XX)

        token_data = response.json()
        print("Access Token received.")
        access_token = token_data.get('access_token')
        return access_token

    except requests.exceptions.RequestException as e:
        print(f"Error getting access token: {e}")
        if response is not None:
            print(f"Response status code: {response.status_code}")
            print(f"Response text: {response.text}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred during token retrieval: {e}")
        return None

def get_zak():
    '''Gathers the ZAK auth token necessary for zoom'''
    token = get_access_token()
    
    if not token:
        print("Error getting ZAK: no token")
        return None

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    try:
        response = requests.get(ZAK_URL, headers=headers, timeout=15)
        response.raise_for_status() # Raise HTTPError for bad responses

        zak_token = response.json()
        print("ZAK token fetched")

        return zak_token.get("token")

    except requests.exceptions.RequestException as e:
        print(f"Error getting zak token: {e}")
        if response is not None:
            print(f"Response status code: {response.status_code}")
            print(f"Response text: {response.text}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred during zak token retrieval: {e}")
        return None
