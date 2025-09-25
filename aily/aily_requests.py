import os

import requests
import json

def get_tenant_token(app_id, app_secret):
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"

    payload = json.dumps({
        "app_id": app_id,
        "app_secret": app_secret
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)
    return response.json()['tenant_access_token']

def upload_file(token, path):

    url = "https://open.feishu.cn/open-apis/aily/v1/files"

    payload = {}
    files = [
        ('file', ('高能阳历1.jpg', open(path, 'rb'), 'image/jpeg'))
    ]
    headers = {
        'Authorization': f'Bearer {token}'
    }

    response = requests.request("POST", url, headers=headers, data=payload, files=files)

    if response.status_code != 200:
        #删除文件
        os.remove(path)

        print(response.text)
        return response.json()['data']['files'][0]['id']
    else:
        return None


def run_aily_skill(app, skill, file_token, check_point, token):
    url = f"https://open.larkoffice.com/open-apis/aily/v1/apps/{app}/skills/{skill}/start"

    payload = json.dumps({
        "global_variable": {
            "files": [file_token]
        },
        "input": f"{{\"check_point\":\"{check_point}\"}}",
    })
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}',
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)

def run_aily_skill_batch_file(app, skill, file_tokens, check_point, token):
    url = f"https://open.larkoffice.com/open-apis/aily/v1/apps/{app}/skills/{skill}/start"

    payload = json.dumps({
        "global_variable": {
            "files": file_tokens
        },
        "input": f"{{\"check_point\":\"{check_point}\"}}",
    })
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}',
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)