import os

import requests
import json

def upload_file(token, filename):

    url = "https://open.feishu.cn/open-apis/aily/v1/files"

    payload = {}

    headers = {
        'Authorization': f'Bearer {token}'
    }

    # 替换原来的 files 定义和 requests 请求部分
    with open(filename, 'rb') as file_obj:  # 用with打开文件，自动管理关闭
        files = [
            ('file', (filename, file_obj, 'image/jpeg'))
        ]
        response = requests.request("POST", url, headers=headers, data=payload, files=files)

    print(response.status_code)
    if response.status_code == 200:
        #删除文件
        os.remove(filename)
        print(response.json()['data']['files'][0]['id'])
        return response.json()['data']['files'][0]['id']
    else:
        print(response.text)
        return None


def run_aily_skill(app, skill, file_token, check_point, token):
    url = f"https://open.feishu.cn/open-apis/aily/v1/apps/{app}/skills/{skill}/start"

    payload = json.dumps({
        "global_variable": {
            "files": file_token
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
    url = f"https://open.feishu.cn/open-apis/aily/v1/apps/{app}/skills/{skill}/start"

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


if __name__ == '__main__':
    upload_file(token="t-g104a4eKGXSYS7GWYXCFG4RDPUZMTOR4RNDYQ2LY", path="../screenshot/screenshot_1759561764.png")
