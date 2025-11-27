from typing import List

from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.schedulers.blocking import BlockingScheduler

from basic.lark.base import batch_get_records
from basic.model.camera import Camera
from scheduler.tasks import screenshot_camera, key_frame_camera

from basic.util.configurator import get_aily_env, get_use_aily, get_capture_source
from basic.util.timeutil import get_timestamp

# 完成截图后删除截图图片

# 统一使用 basic.util.timeutil.get_timestamp

# 工作时间判断逻辑已在 scheduler/tasks.py 统一实现

# 启动应用
if __name__ == '__main__':
    app_id, app_secret, base_token, camera_table_id, record_table_id, app, skill, path = get_aily_env()
    use_aily = get_use_aily()
    # 从配置读取抓帧来源（camera/screenshot），缺省或非法值回退为 camera
    capture_source = get_capture_source()

    # 获取监控配置信息
    cameras: List[Camera] = batch_get_records(app_id, app_secret, base_token, camera_table_id)

    # 配置线程池，设置更大的容量（例如 20 个线程）
    executors = {
        'default': ThreadPoolExecutor(20)  # 调整此处数值
    }

    # 创建调度器（BlockingScheduler会阻塞主线程）
    scheduler = BlockingScheduler(executors=executors)

    print(f"[{get_timestamp()}] 共获取到 {len(cameras)} 个摄像头配置")

    for camera in cameras:
        print(f"[{get_timestamp()}] 配置摄像头: {camera.code}, 频率: {camera.frequency}秒")
        
        # 添加定期任务，时间判断在任务函数内部进行
        if camera.key_frames == "开启":
            # 任务参数含义说明：
            # app_id           Aily 应用 AppID，用于获取租户 token
            # app_secret       Aily 应用 Secret
            # app              Aily 应用标识（app），用于触发技能
            # skill            技能 ID，用于触发具体处理逻辑
            # path             本地截图保存目录（来自配置）
            # camera           摄像头配置对象（编码、link、频率、检测集等）
            # use_aily         上传路径开关：true 走 Aily；false 走多维表格
            # base_token       多维表格 app_token
            # camera_table_id  摄像头配置表 table_id
            # record_table_id  图片记录表 table_id
            # capture_source   抓帧来源：'camera'（摄像头）或 'screenshot'（桌面截图）
            scheduler.add_job(
                key_frame_camera,
                "date",
                args=(app_id, app_secret, app, skill, path, camera),
                kwargs={
                    "use_aily": use_aily,
                    "base_token": base_token,
                    "record_table_id": record_table_id,
                    "capture_source": capture_source,
                }
            )
        else:
            # 普通摄像头添加定时任务
            # 任务参数含义说明同上（见关键帧任务注释）
            scheduler.add_job(
                screenshot_camera,
                "interval",
                seconds=camera.frequency,
                args=(app_id, app_secret, app, skill, path, camera),
                kwargs={
                    "use_aily": use_aily,
                    "base_token": base_token,
                    "record_table_id": record_table_id,
                    "capture_source": capture_source,
                },
                max_instances=5,
                misfire_grace_time=300
        )

    try:
        print("启动间隔调度器...")
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass
