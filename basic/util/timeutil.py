import datetime

def get_timestamp():
    """返回统一格式的时间戳字符串"""
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

