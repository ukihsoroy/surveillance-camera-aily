from typing import List
import datetime
import time
import sys
import os
import threading

# 添加当前目录到系统路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from basic.lark.base import batch_get_records
from basic.model.camera import Camera
from scheduler.tasks import screenshot_camera, key_frame_camera

from basic.util.configurator import get_aily_env

# 改进的调度器实现，支持多线程执行
class BlockingScheduler:
    def __init__(self):
        self.jobs = []
        self.running = True
        self.threads = []
    
    def add_job(self, func, trigger, seconds=None, max_instances=1, id=None, args=None):
        job = {
            'func': func,
            'trigger': trigger,
            'seconds': seconds,
            'id': id,
            'args': args or [],
            'max_instances': max_instances,
            'active_instances': 0
        }
        self.jobs.append(job)
    
    def _job_wrapper(self, job):
        """任务包装器，处理异常并管理活动实例计数"""
        job['active_instances'] += 1
        try:
            job['func'](*job['args'])
        except Exception as e:
            print(f"[{get_timestamp()}] 任务 {job['id']} 执行失败: {str(e)}")
        finally:
            job['active_instances'] -= 1
    
    def _start_date_job(self, job):
        """启动一次性任务"""
        thread = threading.Thread(target=self._job_wrapper, args=(job,), daemon=True)
        thread.start()
        self.threads.append(thread)
        # 从任务列表中移除已执行的一次性任务
        if job in self.jobs:
            self.jobs.remove(job)
    
    def _start_interval_job(self, job):
        """启动间隔任务的执行线程"""
        def interval_executor():
            while self.running:
                if job['active_instances'] < job['max_instances']:
                    thread = threading.Thread(target=self._job_wrapper, args=(job,), daemon=True)
                    thread.start()
                    self.threads.append(thread)
                time.sleep(job['seconds'])
        
        thread = threading.Thread(target=interval_executor, daemon=True)
        thread.start()
        self.threads.append(thread)
    
    def start(self):
        try:
            # 启动所有任务
            for job in list(self.jobs):  # 使用副本以避免修改列表时的问题
                if job['trigger'] == 'date':
                    # 为每个一次性任务创建独立线程
                    self._start_date_job(job)
                elif job['trigger'] == 'interval' and job['seconds'] > 0:
                    # 为每个间隔任务创建独立的调度线程
                    self._start_interval_job(job)
            
            # 主循环保持运行，等待中断
            while self.running:
                time.sleep(1)
                # 清理已完成的线程
                self.threads = [t for t in self.threads if t.is_alive()]
                
                # 检查是否还有任务
                if not self.jobs and not self.threads:
                    break
        except KeyboardInterrupt:
            self.running = False
            # 等待所有线程完成
            for thread in self.threads:
                if thread.is_alive():
                    thread.join(timeout=1.0)  # 给予一定时间让线程优雅退出

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

def create_camera_task(task_func, app_id, app_secret, app, skill, path, camera):
    """
    创建摄像头任务的闭包函数，在执行前进行工作时间检查
    
    Args:
        task_func: 原始任务函数（screenshot_camera或key_frame_camera）
        app_id, app_secret, app, skill, path: 应用配置参数
        camera: 摄像头对象，包含工作时间配置
        
    Returns:
        包装后的任务函数
    """
    def task():
        # 检查工作时间
        if not is_work_time(camera.start_time, camera.end_time):
            print(f"[{get_timestamp()}] 摄像头 {camera.code} 非工作时间，跳过执行")
            return None
        
        print(f"[{get_timestamp()}] 执行摄像头 {camera.code} 任务")
        try:
            result = task_func(app_id, app_secret, app, skill, path, camera)
            print(f"[{get_timestamp()}] 摄像头 {camera.code} 任务完成")
            return result
        except Exception as e:
            print(f"[{get_timestamp()}] 摄像头 {camera.code} 任务异常: {str(e)}")
            return None
    
    return task

def start_keyframe_thread(app_id, app_secret, app, skill, path, camera):
    """
    为关键帧摄像头创建独立的后台线程
    
    Args:
        app_id, app_secret, app, skill, path: 应用配置参数
        camera: 摄像头对象
    """
    def keyframe_worker():
        print(f"[{get_timestamp()}] 关键帧摄像头 {camera.code} 线程启动")
        # 这里不直接调用key_frame_camera，而是在下面的修改中让key_frame_camera支持单次执行
        # key_frame_camera函数将在tasks.py中修改为单次执行模式
        # 这里保持循环逻辑，确保关键帧任务持续运行
        while True:
            if is_work_time(camera.start_time, camera.end_time):
                try:
                    # 调用修改后的key_frame_camera函数（单次执行）
                    key_frame_camera(app_id, app_secret, app, skill, path, camera)
                except Exception as e:
                    print(f"[{get_timestamp()}] 关键帧摄像头 {camera.code} 任务异常: {str(e)}")
            else:
                print(f"[{get_timestamp()}] 关键帧摄像头 {camera.code} 非工作时间，跳过执行")
            # 关键帧检测间隔，使用较小的间隔以保证实时性
            time.sleep(3)
    
    # 创建并启动线程
    thread = threading.Thread(target=keyframe_worker, daemon=True)
    thread.start()
    print(f"[{get_timestamp()}] 关键帧摄像头 {camera.code} 线程已创建")
    return thread

# 启动应用
if __name__ == '__main__':
    app_id, app_secret, base_token, table_id, app, skill, path = get_aily_env()

    # 获取监控配置信息
    cameras: List[Camera] = batch_get_records(app_id, app_secret, base_token, table_id)

    # 创建调度器
    scheduler = BlockingScheduler()

    # 存储关键帧线程的列表
    keyframe_threads = []
    
    print(f"[{get_timestamp()}] 共获取到 {len(cameras)} 个摄像头配置")

    for camera in cameras:
        print(f"[{get_timestamp()}] 配置摄像头: {camera.code}, 频率: {camera.frequency}秒")
        
        if camera.key_frames == "开启":
            # 为关键帧摄像头创建独立线程
            thread = start_keyframe_thread(app_id, app_secret, app, skill, path, camera)
            keyframe_threads.append(thread)
        else:
            # 为普通截图任务创建包装器并添加到调度器
            wrapped_task = create_camera_task(screenshot_camera, app_id, app_secret, app, skill, path, camera)
            scheduler.add_job(
                wrapped_task,
                "interval",
                seconds=camera.frequency,
                max_instances=5,
                id=f"{camera.code}_screenshot"
            )

    try:
        print("启动调度器...")
        # 启动调度器处理普通任务
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        # 设置调度器停止标志
        scheduler.running = False
        # 这里不需要显式停止关键帧线程，因为它们是daemon线程，主程序退出时会自动终止
    finally:
        print("调度器已关闭")