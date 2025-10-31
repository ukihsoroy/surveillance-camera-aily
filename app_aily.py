from typing import List

from basic.lark.base import batch_get_records
from basic.model.camera import Camera
from scheduler.tasks import screenshot_camera, key_frame_camera
from apscheduler.schedulers.blocking import BlockingScheduler

from basic.util.configurator import get_aily_env, get_apaas_env

# 启动应用
if __name__ == '__main__':
    app_id, app_secret, base_token, table_id, app, skill, path = get_aily_env()

    # 获取监控配置信息
    cameras: List[Camera] = batch_get_records(app_id, app_secret, base_token, table_id)

    # 创建调度器（BlockingScheduler会阻塞主线程）
    scheduler = BlockingScheduler()

    print(len(cameras))

    for camera in cameras:
        print(camera.frequency, camera.count, camera.code, camera.link)
        if camera.key_frames == "开启":
            scheduler.add_job(
                key_frame_camera,
                "date",
                args=(app_id, app_secret, app, skill, path, camera)
            )
        else:
            scheduler.add_job(
                screenshot_camera,
                "interval",
                seconds=camera.frequency,
                max_instances=5,
                args=(app_id, app_secret, app, skill, path, camera)
            )


    try:
        print("启动间隔调度器...")
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass


