from typing import List
import datetime

from apscheduler.executors.pool import ThreadPoolExecutor
from basic.lark.base import batch_get_records
from basic.model.camera import Camera
from scheduler.tasks import screenshot_camera, key_frame_camera
from apscheduler.schedulers.blocking import BlockingScheduler

from basic.util.configurator import get_aily_env

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

# 启动应用
if __name__ == '__main__':
    app_id, app_secret, base_token, camera_table_id, record_table_id, app, skill, path = get_aily_env()

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
            scheduler.add_job(
                key_frame_camera,
                "date",
                args=(app_id, app_secret, app, skill, path, camera, True)
            )
        else:
            # 普通摄像头添加定时任务
            scheduler.add_job(
                screenshot_camera,
                "interval",
                seconds=camera.frequency,
                args=(app_id, app_secret, app, skill, path, camera, True),  # 设置为使用多维表格
                max_instances=5,
                misfire_grace_time=300
        )

    try:
        print("启动间隔调度器...")
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass


