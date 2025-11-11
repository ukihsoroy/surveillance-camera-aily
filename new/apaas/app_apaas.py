from typing import List

from basic.lark.apaas import get_camera_list
from basic.lark.tokens import get_apaas_token
from basic.model.camera import Camera
from scheduler.tasks import screenshot_camera_apaas
from apscheduler.schedulers.blocking import BlockingScheduler

from basic.util.configurator import get_apaas_env

# 启动应用
if __name__ == '__main__':
    path, client_id, client_secret, namespace = get_apaas_env()
    token = get_apaas_token(client_id, client_secret)
    # 获取监控配置信息
    cameras: List[Camera] = get_camera_list(namespace, token)

    # 创建调度器（BlockingScheduler会阻塞主线程）
    scheduler = BlockingScheduler()

    print(len(cameras))

    for camera in cameras:
        print(camera.frequency, camera.count, camera.code, camera.link)
        scheduler.add_job(
            screenshot_camera_apaas,
            "interval",
            seconds=camera.frequency,
            max_instances=5,
            args=(client_id, client_secret, path, camera, namespace)
        )
    try:
        print("启动间隔调度器...")
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass


