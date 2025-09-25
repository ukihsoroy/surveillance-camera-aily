import cv2
import time

#链接摄像头视频流，截取视频帧数
#输入是摄像头ip地址
#输出要注意图片保存地址
def camera_screen(ip, path):

    # 打开视频文件
    video = cv2.VideoCapture(ip)

    # 读取视频的第一帧
    ret, frame = video.read()

    # 如果读取成功，则将第一帧保存为图像文件
    # 获取当前时间戳
    timestamp = int(time.time())
    file_name = path + 'camera_{}.jpg'.format(timestamp)
    is_written = False
    if ret:
        is_written = cv2.imwrite(file_name, frame)
        print(file_name)
    else:
        print('Failed to read video frame')
    # 释放视频对象
    video.release()

    if is_written:
        return file_name
    else:
        return None



import configparser
if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('config.ini')
    ip = config['camera']['ip']
    path = config['app']['path']
    name = camera_screen(ip, path)
    print(name)