import random

import cv2
import time

#链接摄像头视频流，截取视频帧数
#输入是摄像头ip地址
#输出要注意图片保存地址
def camera_screen(link, path):

    # 打开视频文件
    video = cv2.VideoCapture(link)

    # 读取视频的第一帧
    ret, frame = video.read()

    # 随机数
    # 获取当前时间戳
    random_num = random.randint(0, 1000000)
    r = str(time.time()) + str(random_num)

    # filename
    filename = path + 'screenshot_{}.png'.format(r)
    is_written = False
    if ret:
        is_written = cv2.imwrite(filename, frame)
        print(filename)
    else:
        print('Failed to read video frame')
    # 释放视频对象
    video.release()

    if is_written:
        return filename
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