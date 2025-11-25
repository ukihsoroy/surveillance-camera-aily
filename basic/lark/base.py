import os

import requests
from requests_toolbelt import MultipartEncoder

from basic.model.camera import Camera

import json

import lark_oapi as lark
from lark_oapi.api.bitable.v1 import *

def _extract_start_time(value):
    """从多维表格字段解析开始时间字符串，如 '08:00'。
    兼容返回为列表[{'text': '8:00'}]或直接字符串。"""
    if isinstance(value, list) and value:
        first = value[0]
        if isinstance(first, dict):
            return first.get('text') or first.get('value') or str(first)
    return value

def _extract_duration(value):
    """从多维表格字段解析工作时长（小时），返回原始数值或字符串数字。
    兼容返回为列表[{'number': 12}]或直接数值/字符串。"""
    if isinstance(value, list) and value:
        first = value[0]
        if isinstance(first, dict):
            num = first.get('number')
            if num is not None:
                return num
            # 兼容 text 数字
            txt = first.get('text')
            return txt if txt is not None else str(first)
    return value

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
            .field_names(["编码", "link", "频率", "截取", "关键帧", "检测集", "开始时间", "工作时长"])
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
                code=item.fields.get("编码")[0]["text"],
                link=item.fields.get("link"),
                frequency=item.fields.get("频率"),
                count=item.fields.get("截取"),
                key_frames=item.fields.get("关键帧"),
                classes=convert_classes(item.fields.get("检测集"))
            )
            # 将record_id存储为实例属性，以便后续使用
            camera.record_id = item.record_id
            # 存储开始时间与工作时长（新配置）
            camera.start_time = _extract_start_time(item.fields.get("开始时间"))
            camera.end_time = _extract_duration(item.fields.get("工作时长"))
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




def upload_media(file_path, parent_type, parent_node, token):
    """
    上传文件到飞书媒体库
    参考：https://open.feishu.cn/document/server-docs/docs/drive-v1/media/upload_all
    
    Args:
        file_path: 本地文件路径
        parent_type: 上传点类型，如'docx_image', 'docx_file'等
        parent_node: 上传点token，即要上传的云文档的token
        token: access_token
        
    Returns:
        file_token: 上传成功后的文件token
    """
    try:
        file_size = os.path.getsize(file_path)
        # 检查文件大小是否超过20MB限制
        if file_size > 20 * 1024 * 1024:
            print(f"[错误] 文件大小超过20MB限制: {file_size/1024/1024:.2f}MB")
            return None
            
        url = "https://open.feishu.cn/open-apis/drive/v1/medias/upload_all"
        form = {
            'file_name': os.path.basename(file_path),
            'parent_type': parent_type,
            'parent_node': parent_node,
            'size': str(file_size),
            'file': (open(file_path, 'rb'))
        }
        multi_form = MultipartEncoder(form)
        headers = {'Authorization': f'Bearer {token}', 'Content-Type': multi_form.content_type}
        response = requests.request("POST", url, headers=headers, data=multi_form)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('code') == 0:
                return result['data']['file_token']
            else:
                print(f"[错误] 上传文件失败: {result.get('msg', '未知错误')}")
        else:
            print(f"[错误] 上传文件HTTP失败: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"[异常] 上传文件时发生错误: {str(e)}")
    finally:
        # 确保文件被关闭
        if 'form' in locals() and 'file' in form:
            form['file'].close()
    return None

def create_record(app_token, table_id, fields, token):
    """
    在多维表格中新增一条记录
    参考：https://open.feishu.cn/document/server-docs/docs/bitable-v1/app-table-record/create
    
    Args:
        app_token: 多维表格App的唯一标识
        table_id: 多维表格数据表的唯一标识
        fields: 要新增的记录数据，格式为字典
        token: access_token
        
    Returns:
        record_id: 创建成功后的记录ID，失败返回None
    """
    try:
        url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records"
        
        payload = json.dumps({
            "fields": fields
        })
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}',
        }
        
        response = requests.request("POST", url, headers=headers, data=payload)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('code') == 0 and result.get('data'):
                return result['data']['record']['record_id']
            else:
                print(f"[错误] 创建记录失败: {result.get('msg', '未知错误')}")
        else:
            print(f"[错误] 创建记录HTTP失败: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"[异常] 创建记录时发生错误: {str(e)}")
    return None

def batch_update_records(app_token, table_id, records, token):
    """
    批量更新多维表格中的记录
    参考：https://go.feishu.cn/s/61Y-IrQjY02
    
    Args:
        app_token: 多维表格App的唯一标识
        table_id: 多维表格数据表的唯一标识
        records: 要更新的记录列表，每条记录包含record_id和fields
        token: access_token
        
    Returns:
        success: 更新是否成功
    """
    try:
        url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records/batch_update"
        
        payload = json.dumps({
            "records": records
        })
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}',
        }
        
        response = requests.request("POST", url, headers=headers, data=payload)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('code') == 0:
                return True
            else:
                print(f"[错误] 批量更新记录失败: {result.get('msg', '未知错误')}")
        else:
            print(f"[错误] 批量更新记录HTTP失败: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"[异常] 批量更新记录时发生错误: {str(e)}")
    return False




# 保留兼容性的insert_records函数，现在使用create_record函数实现
def insert_records(app_token, table_id, fields, token):
    """
    插入记录到多维表格（兼容旧接口）
    """
    return create_record(app_token, table_id, fields, token)


if __name__ == '__main__':
    r = batch_get_records("cli_a82797a53f67500e", "", "A4mTbsRreagi4AsZJAicx1eynZb", "tblfvjN6sZrYBUuc", page_token=None)
    print(r)
