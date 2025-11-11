import os
import time
import logging
from datetime import datetime

from basic.lark.apaas import upload_image, insert_review_record
from basic.lark.tokens import get_apaas_token
from basic.model.camera import Camera
from source.screenshot import fullscreen

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# 批量截取图片
def screenshot_camera_apaas(client_id, client_secret, path, camera: Camera, namespace):
    print(f"间隔任务执行1：{datetime.now().strftime('%H:%M:%S')}")
    token = get_apaas_token(client_id, client_secret)
    filenames = []

    # 截取图片
    # file_name = camera_screen(camera.link, path)

    file_name = fullscreen(path)
    print(file_name)

    # 上传图片
    image = upload_image(token, file_name)

    # 按照频率/次数 等待
    # if camera.count != 1:
    #     time.sleep(camera.frequency/camera.count)

    # 插入记录
    resp = insert_review_record(namespace, token, camera.record_id, image)

    print(resp)

# apaas版本不包含aily相关功能
def screenshot_camera(*args, **kwargs):
    raise NotImplementedError("This function is not implemented in Apaas version")

def key_frame_camera(*args, **kwargs):
    raise NotImplementedError("This function is not implemented in Apaas version")


if __name__ == '__main__':
    for i in range(1):
        print(1)