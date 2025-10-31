import os

import requests
import json

from basic.model.camera import Camera


def get_camera_list(namespace, tenant_token):
    url = f"https://ae-openapi.feishu.cn/v1/data/namespaces/{namespace}/objects/camera/records_query"
    payload = ("{\"need_total_count\":false,\"select\":[\"_id\",\"monitoringPoint\",\"frequency\",\"count\",\"link\"],\"filter\":{\"conditions\":[{"
               "\"operator\":\"equals\",\"left\":{\"type\":\"metadataVariable\",\"settings\":\"{\\\"fieldPath\\\":[{"
               "\\\"fieldApiName\\\": \\\"status\\\",\\\"objectApiName\\\": \\\"status\\\"}]}\"},\"right\":{"
               "\"type\":\"constant\",\"settings\":\"{\\\"data\\\":\\\"online\\\"}\"}}],\"expression\":\"1\"},"
               "\"order_by\":[{\"field\":\"_id\",\"direction\":\"desc\"}],"
               "\"use_page_token\":false,\"offset\":0,\"page_token\":\"\",\"page_size\":100,"
               "\"query_deleted_record\":false}")

    headers = {
        "Authorization": tenant_token,
        "Content-Type": "application/json"
    }

    print(json.dumps(payload))

    response = requests.request("POST", url, headers=headers, data=payload.encode("utf-8"))

    cameras = []

    # 处理失败返回
    if not response.status_code == 200:
        print("error: " + response.text)
        return cameras

    if response.json() is not None and response.json()["data"]["items"] is not None:
        for item in response.json()["data"]["items"]:

            camera = Camera(
                record_id=item["_id"],
                code=item["monitoringPoint"],
                link=item["link"],
                frequency=int(item["frequency"]),
                count=int(item["count"]),
                key_frames=None,
                classes=None
            )
            cameras.append(camera)
    print(cameras)
    return cameras

def insert_review_record(namespace, tenant_token, camera_id, image):
    url = f"https://ae-openapi.feishu.cn/v1/data/namespaces/{namespace}/objects/reviewRecord/records"
    payload = "{\"record\":{\"monitoringImage\":[{\"mime_type\":\"" + image["type"] + "\",\"name\":\"" + image["name"] + "\",\"id\":\"" + image["fileId"] + "\",\"size\":\"" + str(image["size"]) + "\"}],\"camera\":{\"_id\":\"" + camera_id + "\"}}}}"
    headers = {
        "Authorization": tenant_token,
        "Content-Type": "application/json"
    }

    print(json.dumps(payload))

    response = requests.request("POST", url, headers=headers, data=payload.encode('utf-8'))

    print(response.text)


def upload_image(tenant_token, image):
    url = "https://ae-openapi.feishu.cn/api/attachment/v1/files"
    headers = {
        "Authorization": tenant_token
    }

    # 替换原来的 files 定义和 requests 请求部分
    with open(image, 'rb') as file_obj:  # 用with打开文件，自动管理关闭
        files = [
            ('file', (image, file_obj))
        ]
        response = requests.request("POST", url, headers=headers, files=files)

    print(response.status_code)
    if response.status_code == 200:
        # 删除文件
        # os.remove(image)
        print(response.json())

        resp = response.json()['data']
        return resp

    else:
        print(response.text)
        return None


if __name__ == '__main__':
    namespace = "package_b84380__c"
    tenant_token = "T:24f9d118238444e2b304.eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJBcHBJRCI6ImNfZTM3M2FmZmY3ZDg2NGIyMjk0YWQiLCJUZW5hbnROYW1lIjoiZXQ2c3U2dzk1NiIsIlRlbmFudEtleSI6IiIsIlRlbmFudElEIjoxNDY5OTksIkVudiI6Im9ubGluZSIsIkFwcFR5cGUiOjMsIk5hbWVzcGFjZSI6InBhY2thZ2VfYjg0MzgwX19jIiwiYXZlciI6IiIsInNvdXJjZSI6InBhZ2UiLCJMYW5lIjoiIiwiZXhwIjoxNzYyNDk2MzY2NjQzfQ.O6YSu6ZCLObgNHZPXM8kZ1vZATSG150Qh50z8UiXZ78"
    # get_camera_list(namespace, tenant_token)

    image = upload_image(tenant_token, "./demo.jpg")
    insert_review_record(namespace, tenant_token, "100", image)

    print(image)
