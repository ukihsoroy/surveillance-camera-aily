import threading

class Camera:
    def __init__(self, code, link, frequency, count, key_frames, classes):
        self.code = code
        self.link = link
        self.frequency = frequency
        self.count = count
        self.key_frames = key_frames
        self.classes = classes
        self.frames_count = 0
        # 添加工作时间相关属性，默认为None
        self.start_time = None
        self.end_time = None
        # 添加记录ID属性，用于后续操作
        self.record_id = None
        # 添加线程锁，保护共享资源
        self.lock = threading.RLock()
    
    def get_frames_count(self):
        """线程安全地获取frames_count"""
        with self.lock:
            return self.frames_count
    
    def set_frames_count(self, value):
        """线程安全地设置frames_count"""
        with self.lock:
            self.frames_count = value
    
    def compare_and_set_frames_count(self, expected, new_value):
        """
        线程安全地比较并设置frames_count
        
        Args:
            expected: 期望的当前值
            new_value: 要设置的新值
            
        Returns:
            bool: 如果值匹配并更新成功返回True，否则返回False
        """
        with self.lock:
            if self.frames_count == expected:
                self.frames_count = new_value
                return True
            return False
