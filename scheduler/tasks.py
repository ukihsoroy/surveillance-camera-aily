import time
from datetime import datetime

from basic.lark.aily import upload_file, run_aily_skill
from basic.lark.token import get_tenant_token
from basic.model.camera import Camera
from source.surveillance import camera_screen
from source.screenshot import fullscreen


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


if __name__ == '__main__':
    for i in range(1):
        print(1)