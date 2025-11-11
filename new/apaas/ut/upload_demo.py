import configparser
import time
import os
from basic.lark.apaas import *
from basic.lark.tokens import get_apaas_token
from source.surveillance import *
from source.screenshot import *

# 启动应用
if __name__ == '__main__':
    # 读取配置文件
    config = configparser.ConfigParser()
    config.read('config.ini')

    # 获取当前文件所在目录的父目录，即项目根目录
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(base_dir, 'config.ini')
    config.read(config_path)

    client_id = config['apaas']['client_id']
    client_secret = config['apaas']['client_secret']
    namespace = config['apaas']['namespace']
    path = config['app']['path']
    record_id = 'demo_record_id'  # 替换为实际的记录ID

    #截取屏幕
    file_name = fullscreen(path)

    # 获取token
    token = get_apaas_token(client_id, client_secret)

    # 上传图片到apaas
    image = upload_image(token, file_name)

    # 插入审核记录
    resp = insert_review_record(namespace, token, record_id, image)
    print("上传结果:", resp)
