import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()

def hakka_translate(text, index):

    # Validate environment variables
    url = os.getenv("HAKKA_TRANS_URL_BASE")
    transUrl = os.getenv("HAKKA_TRANS_URL_TRANS")
    username = os.getenv("HAKKA_TRANS_USERNAME")
    password = os.getenv("HAKKA_TRANS_PASSWORD")

    if not url or not transUrl or not username or not password:
        raise ValueError("Missing one or more required environment variables: HAKKA_TRANS_URL_BASE, HAKKA_TRANS_URL_TRANS, HAKKA_TRANS_USERNAME, HAKKA_TRANS_PASSWORD")

    try:
        # Authenticate and get token
        payload = json.dumps({
            "username": username,
            "password": password,
            "rememberMe": 0
        })
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.request("POST", url, headers=headers, data=payload, verify=False)
        response.raise_for_status()
        token = response.json().get('token')
        if not token:
            raise ValueError("Authentication failed: No token received")
        print(f"token:{token}")

        # Translate text
        payload = json.dumps({
            "input": text
        })
        headers = {
            'Authorization': 'Bearer ' + token,
            'Content-Type': 'application/json'
        }
        response = requests.request("POST", transUrl, headers=headers, data=payload, verify=False)
        response.raise_for_status()
        print(f"translate result : {response.text}")

        # Save translation result
        output_dir = './temp_trans'
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f'translation_{index}.json')
        print(output_path)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(response.json(), f, ensure_ascii=False, indent=4)

    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"API request failed: {e}")
    except ValueError as e:
        raise RuntimeError(f"Error: {e}")