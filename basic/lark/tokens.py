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


if __name__ == '__main__':
    token = get_tenant_token('cli_a82797a53f67500e', '')
    print(token)
