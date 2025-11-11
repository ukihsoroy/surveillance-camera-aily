from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime


def task1():
    print(f"间隔任务执行1：{datetime.now().strftime('%H:%M:%S')}")

def task2():
    print(f"间隔任务执行2：{datetime.now().strftime('%H:%M:%S')}")

if __name__ == "__main__":
    # 创建调度器（BlockingScheduler会阻塞主线程）
    scheduler = BlockingScheduler()

    # 添加任务：间隔5秒执行
    scheduler.add_job(
        task1,
        'interval',  # 间隔触发
        seconds=5  # 间隔时间（秒），支持minutes/hours/days
    )

    # 添加任务：间隔5秒执行
    scheduler.add_job(
        task2,
        'interval',  # 间隔触发
        seconds=5  # 间隔时间（秒），支持minutes/hours/days
    )

    try:
        print("启动间隔调度器...")
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass