import os
import time
import logging
from datetime import datetime

from basic.lark.aily import upload_file, run_aily_skill
from basic.lark.tokens import get_tenant_token
from basic.model.camera import Camera
from channel.yolo.yolov5 import identify
from source.screenshot import fullscreen

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# 批量截取图片
def screenshot_camera(app_id, app_secret, aily_app, aily_skill, path, camera: Camera):
    print(f"间隔任务执行1：{datetime.now().strftime('%H:%M:%S')}")
    token = get_tenant_token(app_id, app_secret)
    filenames = []

    # 循环几次
    for i in range(camera.count):
        # 截取图片
        # file_name = camera_screen(camera.link, path)

        file_name = fullscreen(path)
        print(file_name)

        # 上传图片aily
        filenames.append(upload_file(token, file_name))

        # 按照频率/次数 等待
        if camera.count != 1:
            time.sleep(camera.frequency/camera.count)
    #执行aily技能
    resp = run_aily_skill(aily_app, aily_skill, filenames, camera.code, token)

    print(resp)

# aily版本不包含apaas相关功能


def key_frame_camera(app_id, app_secret, aily_app, aily_skill, path, camera: Camera):
    print(f"间隔任务执行1：{datetime.now().strftime('%H:%M:%S')}")
    token = get_tenant_token(app_id, app_secret)

    while True:
        # 截取图片
        # file_name = camera_screen(camera.link, path)
        file_name = fullscreen(path)
        count = identify(file_name, camera.classes)
        print(count)
        print(file_name)
        # 当统计范围有变化时，处理
        if count != camera.frames_count and count != 0:
            filename = upload_file(token, file_name)
            camera.frames_count = count
            # 执行aily技能
            resp = run_aily_skill(aily_app, aily_skill, [filename], camera.code, token)
            print(resp)
        else:
            # 删除图片
            os.remove(file_name)

        if count == 0:
            camera.frames_count = count

        time.sleep(3)


if __name__ == '__main__':
    for i in range(1):
        print(1)