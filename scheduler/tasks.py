import os
import time
import datetime
import requests

from basic.lark.aily import upload_file, run_aily_skill
from basic.lark.tokens import get_tenant_token
from basic.model.camera import Camera
from channel.yolo.yolov5 import identify
from source.screenshot import fullscreen
from source.surveillance import camera_screen


def get_timestamp():
    """获取格式化的时间戳，用于日志输出"""
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def is_work_time(start_time, end_time):
    """
    判断当前时间是否在工作时间范围内
    
    Args:
        start_time: 开始时间戳（毫秒或秒级）
        end_time: 结束时间戳（毫秒或秒级）
        
    Returns:
        bool: True表示在工作时间内，False表示不在工作时间内
    """
    # 无时间配置时默认为工作时间
    if not start_time or not end_time:
        print(f"[{get_timestamp()}] 警告：摄像头未配置工作时间，默认为工作时间")
        return True
    
    # 获取当前时间
    now = datetime.datetime.now()
    current_time = now.time()
    
    try:
        # 解析时间戳，支持毫秒和秒级
        try:
            # 尝试毫秒级时间戳
            start_dt = datetime.datetime.fromtimestamp(int(start_time) / 1000)
            end_dt = datetime.datetime.fromtimestamp(int(end_time) / 1000)
        except:
            # 尝试秒级时间戳
            start_dt = datetime.datetime.fromtimestamp(int(start_time))
            end_dt = datetime.datetime.fromtimestamp(int(end_time))
        
        # 提取工作时间范围
        start_time_today = start_dt.time()
        end_time_today = end_dt.time()
        
        # 判断当前时间是否在工作时间范围内
        if start_time_today <= end_time_today:
            # 同一天内的时间范围
            in_range = start_time_today <= current_time <= end_time_today
        else:
            # 跨天的时间范围
            in_range = current_time >= start_time_today or current_time <= end_time_today
            
        print(f"[{get_timestamp()}] 工作时间检查: 当前{current_time}, 范围{start_time_today}-{end_time_today}, 结果:{'在' if in_range else '不在'}范围内")
        return in_range
        
    except Exception as e:
        print(f"[{get_timestamp()}] 时间戳解析失败: {str(e)}")
        return False


# 批量截取图片
def screenshot_camera(app_id, app_secret, aily_app, aily_skill, path, camera: Camera, use_aily=True):
    # 检查工作时间
    if not is_work_time(camera.start_time, camera.end_time):
        print(f"[{get_timestamp()}] 摄像头 {camera.code} 非工作时间，跳过执行截图任务")
        return
        
    print(f"[{get_timestamp()}] 执行摄像头 {camera.code} 截图任务")
    token = get_tenant_token(app_id, app_secret)
    filenames = []

    # 循环几次
    for i in range(camera.count):
        # 截取图片
        file_name = camera_screen(camera.link, path)

        # file_name = fullscreen(path)
        print(file_name)

        # 根据参数决定是上传到aily还是保存文件路径
        if use_aily:
            filenames.append(upload_file(token, file_name))
        else:
            # 保存原始文件路径用于上传到多维表格
            filenames.append(file_name)

        # 按照频率/次数 等待
        if camera.count != 1:
            time.sleep(camera.frequency/camera.count)
    # 根据参数决定执行aily技能还是上传到多维表格
    if use_aily:
        # 执行aily技能
        resp = run_aily_skill(aily_app, aily_skill, filenames, camera.code, token)
        print(resp)
    else:
        # 上传到多维表格
        from basic.util.configurator import get_aily_env
        # 获取配置信息，特别是多维表格的token
        _, _, base_token, camera_table_id, record_table_id, _, _ = get_aily_env()

        
        print(f"[{get_timestamp()}] 将图片上传到多维表格")
        for file_name in filenames:
            # 使用我们测试成功的新方法
            success = upload_image_to_bitable(
                base_token,  # 多维表格的 app_token
                record_table_id,    # 正确的 table_id
                file_name,   # 图片路径
                token,       # tenant_access_token
                camera.record_id  # 关联的巡检点位 record_id
            )
            print(f"[{get_timestamp()}] 图片上传{'成功' if success else '失败'}: {file_name}")
            # 上传后删除本地文件
            if success and os.path.exists(file_name):
                os.remove(file_name)

# 从test_upload.py移植过来的，经过验证的上传函数
def upload_image_to_bitable(app_token, table_id, file_path, token, inspection_point_record_id, fields=None):
    """按照正确流程上传图片到多维表格
    1. 先上传素材获取file_token
    2. 然后使用file_token创建新记录
    """
    print(f"[{get_timestamp()}] 开始文件上传流程")

    # 内部函数：上传素材
    def upload_media(file_path, token, app_token):
        url = "https://open.feishu.cn/open-apis/drive/v1/medias/upload_all"
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        
        data = {
            'file_name': file_name,
            'parent_type': 'bitable_image',
            'parent_node': app_token,
            'size': str(file_size),
            'extra': f'{{"drive_route_token":"{app_token}"}}'
        }
        files = {'file': (file_name, open(file_path, 'rb'), 'image/png')}
        headers = {"Authorization": f"Bearer {token}"}

        print(f"[{get_timestamp()}] 准备上传素材，URL: {url}")
        
        try:
            response = requests.post(url, headers=headers, files=files, data=data)
            print(f"[{get_timestamp()}] 素材上传API响应: {response.status_code}, {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 0:
                    file_token = result.get('data', {}).get('file_token')
                    print(f"[{get_timestamp()}] 素材上传成功，file_token: {file_token}")
                    return file_token
                else:
                    print(f"[{get_timestamp()}] 素材上传失败: {result.get('msg', '未知错误')}")
            else:
                print(f"[{get_timestamp()}] 素材上传HTTP失败: {response.status_code}, {response.text}")
        except Exception as e:
            print(f"[{get_timestamp()}] 素材上传时发生异常: {str(e)}")
        return None

    # 内部函数：获取表格字段
    def get_table_fields_inside(app_token, table_id, token):
        url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/fields"
        headers = {"Authorization": f"Bearer {token}"}
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200 and response.json().get('code') == 0:
                return response.json().get('data', {}).get('items', [])
        except Exception as e:
            print(f"[{get_timestamp()}] 获取表格字段时发生异常: {str(e)}")
        return []

    # 1. 上传素材
    print(f"[{get_timestamp()}] 步骤 1: 上传素材 {file_path}")
    file_token = upload_media(file_path, token, app_token)
    if not file_token:
        print(f"[{get_timestamp()}] 素材上传失败，终止流程")
        return False

    # 2. 查找附件字段
    print(f"[{get_timestamp()}] 步骤 2: 查找附件字段")
    if fields is None:
        fields = get_table_fields_inside(app_token, table_id, token)
    
    actual_field_name = None
    file_field_name = "照片" # 硬编码附件字段名
    if fields:
        for field in fields:
            if field.get('type') == 17: # 附件字段类型为 17
                actual_field_name = field.get('field_name')
                print(f"[{get_timestamp()}] 找到附件类型(17)的字段: '{actual_field_name}'")
                break
        if not actual_field_name:
            print(f"[{get_timestamp()}] 警告: 未在表格中找到附件类型的字段。将回退使用指定的字段名 '{file_field_name}'")
            actual_field_name = file_field_name
    else:
        print(f"[{get_timestamp()}] 警告: 无法获取表格字段，将使用指定的字段名 '{file_field_name}'")
        actual_field_name = file_field_name

    # 3. 创建新记录
    print(f"[{get_timestamp()}] 步骤 3: 创建带附件和巡检点位的新记录")
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8",
    }

    # 构造 payload
    payload_fields = {
        actual_field_name: [{"file_token": file_token}]
    }
    
    # 添加巡检点位关联
    if inspection_point_record_id:
        payload_fields["巡检点位"] = [inspection_point_record_id]
        print(f"[{get_timestamp()}] 添加关联巡检点位: {inspection_point_record_id}")

    payload = {"fields": payload_fields}
    
    print(f"[{get_timestamp()}] 准备创建新记录，URL: {url}")

    try:
        response = requests.post(url, headers=headers, json=payload)
        print(f"[{get_timestamp()}] 创建记录API响应: {response.status_code}, {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('code') == 0:
                record_id = result.get('data', {}).get('record', {}).get('record_id')
                print(f"[{get_timestamp()}] 图片上传成功！新记录ID: {record_id}")
                return True
            else:
                print(f"[{get_timestamp()}] 记录创建失败: {result.get('msg', '未知错误')}")
                return False
        else:
            print(f"[{get_timestamp()}] 记录创建HTTP失败: {response.status_code}, {response.text}")
            return False
    except Exception as e:
        print(f"[{get_timestamp()}] 记录创建时发生异常: {str(e)}")
        return False



def key_frame_camera(app_id, app_secret, aily_app, aily_skill, path, camera: Camera, use_aily=True):
    print(f"[{get_timestamp()}] 间隔任务执行：关键帧检测")
    token = get_tenant_token(app_id, app_secret)

    while True:
        # 检查工作时间
        if not is_work_time(camera.start_time, camera.end_time):
            print(f"[{get_timestamp()}] 摄像头 {camera.code} 非工作时间，跳过执行关键帧检测")
            time.sleep(3)
            continue
            
        # 截取图片
        file_name = camera_screen(camera.link, path)
        # file_name = fullscreen(path)
        count = identify(file_name, camera.classes)
        print(f"检测到 {count} 个目标")
        print(file_name)
        # 当统计范围有变化时，处理
        if count != camera.frames_count and count != 0:
            if use_aily:
                # 上传到aily并执行技能
                filename = upload_file(token, file_name)
                camera.frames_count = count
                # 执行aily技能
                resp = run_aily_skill(aily_app, aily_skill, [filename], camera.code, token)
                print(resp)
            else:
                # 上传到多维表格
                from basic.lark.base import update_record_with_file
                from basic.util.configurator import get_aily_env
                # 获取配置信息，特别是多维表格的token
                # 上传到多维表格
                from basic.util.configurator import get_aily_env
                # 获取配置信息，特别是多维表格的token
                _, _, base_token, camera_table_id, record_table_id, _, _ = get_aily_env()
                print(f"[{get_timestamp()}] 将关键帧图片上传到多维表格，记录ID: {camera.record_id}")
                camera.frames_count = count
                # 使用配置文件中的base_token和table_id
                success = update_record_with_file(
                    base_token,  # 使用多维表格的token
                    camera_table_id,  # 使用配置文件中的table_id
                    camera.record_id,
                    "照片",  # 多维表格中的附件字段名称
                    file_name,
                    token
                )
                print(f"[{get_timestamp()}] 关键帧图片上传{'成功' if success else '失败'}: {file_name}")
                # 上传后删除本地文件
                if os.path.exists(file_name):
                    os.remove(file_name)
        else:
            # 删除图片
            os.remove(file_name)

        if count == 0:
            camera.frames_count = count

        time.sleep(3)


if __name__ == '__main__':
    for i in range(1):
        print(1)