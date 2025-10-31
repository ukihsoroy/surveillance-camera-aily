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


def get_apaas_token(client_id, client_secret):
    url = "https://ae-openapi.feishu.cn/auth/v1/appToken"
    payload = {
        "clientId": client_id,
        "clientSecret": client_secret
    }
    headers = {
        "Content-Type": "application/json"
    }

    response = requests.request("POST", url, headers=headers, data=json.dumps(payload).encode('utf-8'))

    return response.json()['data']['accessToken']


if __name__ == '__main__':
    token = get_apaas_token('c_e373afff7d864b2294ad', '')
    print(token)