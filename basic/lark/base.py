import os

import requests
from requests_toolbelt import MultipartEncoder

from basic.model.camera import Camera

import json

import lark_oapi as lark
from lark_oapi.api.bitable.v1 import *

def batch_get_records(app_id, app_secret, base_id, table_id, page_token=None):
    # 创建client
    client = lark.Client.builder() \
        .app_id(app_id) \
        .app_secret(app_secret) \
        .log_level(lark.LogLevel.DEBUG) \
        .build()

    # 构造请求对象
    request: SearchAppTableRecordRequest = SearchAppTableRecordRequest.builder() \
        .app_token(base_id) \
        .table_id(table_id) \
        .user_id_type("open_id") \
        .page_token("" if page_token is None else page_token) \
        .page_size(10) \
        .request_body(SearchAppTableRecordRequestBody.builder()
            .field_names(["编码", "link", "频率", "截取", "关键帧", "检测集"])
            .automatic_fields(True)
            .filter(FilterInfo.builder()
               .conjunction("and")
               .conditions([Condition.builder().field_name("状态").operator("is").value(["有效"]).build()])
               .build())
            .build()) \
        .build()

    # 发起请求
    response: SearchAppTableRecordResponse = client.bitable.v1.app_table_record.search(request)

    cameras = []

    # 处理失败返回
    if not response.success():
        lark.logger.error(
            f"client.bitable.v1.app_table_record.search failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}, resp: \n{json.dumps(json.loads(response.raw.content), indent=4, ensure_ascii=False)}")
        return cameras

    # 处理业务结果
    lark.logger.info(lark.JSON.marshal(response.data, indent=4))

    if response.data is not None and response.data.items is not None:
        for item in response.data.items:
            camera = Camera(
                record_id=item.record_id,
                code=item.fields.get("编码")[0]["text"],
                link=item.fields.get("link"),
                frequency=item.fields.get("频率"),
                count=item.fields.get("截取"),
                key_frames=item.fields.get("关键帧"),
                classes=convert_classes(item.fields.get("检测集"))
            )
            cameras.append(camera)

    return cameras


def convert_classes(classes):
    if classes is None: return []
    # 定义类别到数字的映射字典
    class_mapping = {
        "人": 0,
        "车": 2,
        "卡车": 7
    }
    # 遍历列表，通过字典映射转换每个元素
    for i in range(len(classes)):
        classes[i] = class_mapping[classes[i]]
    return classes




def upload_media(base_token ,token):
    file_path = "path/demo.jpeg"
    file_size = os.path.getsize(file_path)
    url = "https://open.feishu.cn/open-apis/drive/v1/medias/upload_all"
    form = {
        'file_name': 'demo.jpeg',
        'parent_type': 'doc_image',
        'parent_node': base_token,
        'size': str(file_size),
        'file': (open(file_path, 'rb'))
    }
    multi_form = MultipartEncoder(form)
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': multi_form.content_type}
    response = requests.request("POST", url, headers=headers, data=multi_form)
    return response.json()['data']['file_token']


def insert_records(app_token, table_id, records, token):
    url = f"https://open.larkoffice.com/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records"

    payload = json.dumps({
        "fields": {
            "人员": [
                {
                    "id": "ou_2910013f1e6456f16a0ce75ede9abcef"
                },
                {
                    "id": "ou_e04138c9633dd0d2ea166d79f54abcef"
                }
            ],
            "任务名称": "拜访潜在客户",
            "单向关联": [
                "recHTLvO7x",
                "recbS8zb2m"
            ],
            "单选": "选项1",
            "双向关联": [
                "recHTLvO7x",
                "recbS8zb2m"
            ],
            "地理位置": "116.397755,39.903179",
            "复选框": True,
            "多选": [
                "选项1",
                "选项2"
            ],
            "工时": 10,
            "日期": 1674206443000,
            "条码": "+$$3170930509104X512356",
            "电话号码": "1302616xxxx",
            "群组": [
                {
                    "id": "oc_cd07f55f14d6f4a4f1b51504e7e97f48"
                }
            ],
            "评分": 3,
            "货币": 3,
            "超链接": {
                "link": "https://www.feishu.cn/product/base",
                "text": "飞书多维表格官网"
            },
            "进度": 0.25,
            "附件": [
                {
                    "file_token": "DRiFbwaKsoZaLax4WKZbEGCccoe"
                },
                {
                    "file_token": "BZk3bL1Enoy4pzxaPL9bNeKqcLe"
                },
                {
                    "file_token": "EmL4bhjFFovrt9xZgaSbjJk9c1b"
                },
                {
                    "file_token": "Vl3FbVkvnowlgpxpqsAbBrtFcrd"
                }
            ]
        }

    })
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}',
    }

    response = requests.request("POST", url, headers=headers, data=payload)


if __name__ == '__main__':
    r = batch_get_records("cli_a82797a53f67500e", "", "A4mTbsRreagi4AsZJAicx1eynZb", "tblfvjN6sZrYBUuc", page_token=None)
    print(r)
