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
from basic.util.timeutil import get_timestamp

# 统一使用 basic.util.timeutil.get_timestamp 来获取时间戳

"""解析 'HH:MM' 或 'H' 形式为 (hour, minute)。解析失败返回 (None, None)。"""
def _parse_hhmm(time_str):
    norm = str(time_str).strip()
    if not norm:
        return None, None
    parts = norm.split(":") if ":" in norm else [norm]
    try:
        h = int(parts[0])
    except Exception:
        return None, None
    m = 0
    if len(parts) > 1:
        try:
            m = int(parts[1])
        except Exception:
            m = 0
    if not (0 <= h < 24) or not (0 <= m < 60):
        return None, None
    return h, m

"""解析工作时长为浮点小时，支持数字与字符串（兼容全角数字）。失败返回 None。"""
def _parse_duration_hours(val):
    if isinstance(val, (int, float)):
        num = float(val)
    else:
        s = str(val).strip()
        if not s:
            return None
        try:
            num = float(s)
        except Exception:
            return None
    return num if num > 0 else None

"""
新版工作时间判断：
- start_time: 'HH:MM' 字符串
- duration_hours: 工作时长（小时，支持 int/float/数字字符串）
"""
def is_work_time(start_time, duration_hours):
    # 缺省或空值：默认为非工作时间
    if start_time is None or duration_hours is None:
        print(f"[{get_timestamp()}] 警告：缺少开始时间或工作时长，默认为非工作时间")
        return False

    now = datetime.datetime.now()
    current_time = now.time()

    try:
        # 统一解析与校验开始时间与工作时长
        start_h, start_m = _parse_hhmm(start_time)
        dur = _parse_duration_hours(duration_hours)

        if start_h is None or start_m is None:
            print(f"[{get_timestamp()}] 开始时间格式错误或超出范围: {start_time}，默认为非工作时间")
            return False
        if dur is None or dur <= 0:
            print(f"[{get_timestamp()}] 工作时长配置异常: {duration_hours}，默认为非工作时间")
            return False
        if dur > 24:
            print(f"[{get_timestamp()}] 工作时长超过上限(24h): {duration_hours}，默认为非工作时间")
            return False

        start_dt = datetime.datetime.combine(now.date(), datetime.time(hour=start_h, minute=start_m))
        end_dt = start_dt + datetime.timedelta(hours=dur)
        start_time_today = start_dt.time()
        end_time_today = end_dt.time()

        if start_time_today <= end_time_today:
            in_range = start_time_today <= current_time <= end_time_today
        else:
            in_range = current_time >= start_time_today or current_time <= end_time_today

        return in_range
    except Exception as e:
        print(f"[{get_timestamp()}] 工作时间解析失败: {str(e)}，默认为非工作时间")
        return False


# 批量截取图片

# user_aily抽到ini里面

def screenshot_camera(app_id, app_secret, aily_app, aily_skill, path, camera: Camera, use_aily, base_token, record_table_id, capture_source):

    # 检查工作时间
    if not is_work_time(camera.start_time, camera.end_time):
        print(f"[{get_timestamp()}] 摄像头 {camera.code} 非工作时间，跳过执行截图任务")
        return
        
    print(f"[{get_timestamp()}] 执行摄像头 {camera.code} 截图任务")
    token = get_tenant_token(app_id, app_secret)
    filenames = []

    # 步骤 1: 统一收集所有截图的本地文件路径
    print(f"[{get_timestamp()}] 步骤 1: 开始收集 {camera.count} 张截图...")
    for i in range(camera.count):
        # 按配置源抓帧
        if capture_source == 'screenshot':
            file_name = fullscreen(path)
        else:
            file_name = camera_screen(camera.link, path)

        if file_name:
            print(f"  截图成功: {file_name}")
            filenames.append(file_name)
        else:
            print(f"  截图失败，跳过本次")

        if camera.count > 1:
            time.sleep(camera.frequency / camera.count)

    if not filenames:
        print(f"[{get_timestamp()}] 未能成功截取任何图片，任务结束")
        return

    # 步骤 2: 循环结束后，根据 use_aily 统一处理收集到的文件
    print(f"[{get_timestamp()}] 步骤 2: 收集完成，开始处理 {len(filenames)} 个文件...")
    if use_aily:
        # Aily 路径：批量上传，然后触发一次技能
        aily_tokens = []
        for file_name in filenames:
            uploaded_id = upload_file(token, file_name)
            if uploaded_id:
                aily_tokens.append(uploaded_id)

            # 上传后无论成功与否都删除本地文件
            if os.path.exists(file_name):
                os.remove(file_name)

        if aily_tokens:
            print(f"[{get_timestamp()}] Aily 上传完成，触发技能...")
            resp = run_aily_skill(aily_app, aily_skill, aily_tokens, camera.code, token)
            print(resp)
        else:
            print(f"[{get_timestamp()}] 未能成功上传任何文件到Aily，跳过技能触发")
    else:
        # 多维表格路径：逐个上传并删除
        for file_name in filenames:
            success = upload_image_to_bitable(
                base_token,
                record_table_id,
                file_name,
                token,
                camera.record_id
            )
            print(f"[{get_timestamp()}] 图片上传到多维表格{'成功' if success else '失败'}: {file_name}")
            # 上传成功后删除本地文件
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



def key_frame_camera(app_id, app_secret, aily_app, aily_skill, path, camera: Camera, use_aily, base_token, record_table_id, capture_source):
    print(f"[{get_timestamp()}] 间隔任务执行：关键帧检测")
    token = get_tenant_token(app_id, app_secret)

    while True:
        # 检查工作时间
        if not is_work_time(camera.start_time, camera.end_time):
            print(f"[{get_timestamp()}] 摄像头 {camera.code} 非工作时间，跳过执行关键帧检测")
            time.sleep(3)
            continue
            
        # 按配置源抓帧
        if capture_source == 'screenshot':
            file_name = fullscreen(path)
        else:
            file_name = camera_screen(camera.link, path)
        # 如截图失败，跳过本轮检测
        if not file_name:
            print(f"[{get_timestamp()}] 关键帧截图失败，跳过本轮")
            time.sleep(3)
            continue

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
                # 上传到多维表格：创建记录并关联巡检点位（使用入口传入的配置）
                print(f"[{get_timestamp()}] 将关键帧图片上传到多维表格，关联巡检点位记录ID: {camera.record_id}")
                camera.frames_count = count
                success = upload_image_to_bitable(
                    base_token,
                    record_table_id,
                    file_name,
                    token,
                    camera.record_id
                )
                print(f"[{get_timestamp()}] 关键帧图片上传{'成功' if success else '失败'}: {file_name}")
                # 上传后删除本地文件
                if success and file_name and os.path.exists(file_name):
                    os.remove(file_name)
        else:
            # 删除图片
            if file_name and os.path.exists(file_name):
                os.remove(file_name)

        if count == 0:
            camera.frames_count = count

        time.sleep(3)


if __name__ == '__main__':
    for i in range(1):
        print(1)
