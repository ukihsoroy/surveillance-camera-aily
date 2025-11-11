class Camera:
    def __init__(self, record_id, code, link, frequency, count, key_frames, classes):
        self.record_id = record_id
        self.code = code
        self.link = link
        self.frequency = frequency
        self.count = count
        self.key_frames = key_frames
        self.classes = classes
        self.frames_count = 0
