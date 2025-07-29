import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()

def hakka_translate(text, index):

    url = os.getenv("HAKKA_TRANS_URL_BASE", "")
    transUrl = os.getenv("HAKKA_TRANS_URL_TRANS", "")
    username = os.getenv("HAKKA_TRANS_USERNAME", "")
    password = os.getenv("HAKKA_TRANS_PASSWORD", "")

    payload = json.dumps({
        "username": username,
        "password": password,
        "rememberMe": 0
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload, verify=False)
    token = response.json()['token']
    print(f"token:{token}")

    payload = json.dumps({
        "input": text
    })

    headers = {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", transUrl, headers=headers, data=payload, verify=False)

    print(f"translate result : {response.text}")

    output_dir = 'backend/temp_trans'
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f'translation_{index}.json')
    print(output_path)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(response.json(), f, ensure_ascii=False, indent=4)




