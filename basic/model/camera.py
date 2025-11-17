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
