import os
import time
from datetime import datetime

from basic.lark.aily import upload_file, run_aily_skill
from basic.lark.tokens import get_tenant_token
from basic.model.camera import Camera
from channel.yolo.yolov5 import identify
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


def key_frame_camera(app_id, app_secret, aily_app, aily_skill, path, camera: Camera):
    """
    关键帧摄像头单次检测函数
    
    执行单次截图和对象检测，根据检测结果决定是否触发技能
    
    Args:
        app_id, app_secret, aily_app, aily_skill, path: 应用配置参数
        camera: 摄像头对象
    """
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 关键帧摄像头 {camera.code} 执行单次检测")
    token = get_tenant_token(app_id, app_secret)

    # 截取图片
    file_name = fullscreen(path)
    
    try:
        # 识别对象
        count = identify(file_name, camera.classes)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 摄像头 {camera.code} 检测到 {count} 个目标")
        
        # 获取当前计数（线程安全）
        current_count = camera.get_frames_count()
        
        # 当统计范围有变化时，处理
        if count != current_count and count != 0:
            # 上传图片
            filename = upload_file(token, file_name)
            # 更新检测计数（线程安全）
            camera.set_frames_count(count)
            # 执行aily技能
            resp = run_aily_skill(aily_app, aily_skill, [filename], camera.code, token)
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 摄像头 {camera.code} 技能执行结果: {resp}")
        else:
            # 删除图片
            os.remove(file_name)
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 摄像头 {camera.code} 目标数量无变化，删除图片")

        # 如果检测到0个目标，重置计数（线程安全）
        if count == 0:
            camera.set_frames_count(count)
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 摄像头 {camera.code} 未检测到目标，重置计数")
            
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 摄像头 {camera.code} 检测过程中发生错误: {str(e)}")
        # 发生异常时，尝试删除临时文件
        if os.path.exists(file_name):
            try:
                os.remove(file_name)
            except:
                pass
        raise  # 重新抛出异常，让调用者知道发生了错误


if __name__ == '__main__':
    for i in range(1):
        print(1)