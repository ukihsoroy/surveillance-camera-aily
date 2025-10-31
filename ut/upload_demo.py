from basic.lark.aily import *
from basic.lark.tokens import get_tenant_token
from source.surveillance import *
from source.screenshot import *

# 启动应用
if __name__ == '__main__':
    # 读取配置文件
    config = configparser.ConfigParser()
    config.read('config.ini')

    app_id = config['aily']['app_id']
    app_secret = config['aily']['app_secret']
    app = config['aily']['app']
    skill = config['aily']['skill']
    path = config['app']['path']
    ip = config['camera']['ip']
    batch_image = []

    while True:
        #截取屏幕
        # file_name = fullscreen(path)

        # 链接IP，截取视频帧数
        file_name = camera_screen(ip, path)

        # 获取token
        token = get_tenant_token(app_id, app_secret)

        file_id = upload_file(token, file_name)

        batch_image.append(file_id)
        if len(batch_image) == 10:
            # 调用aily技能
            run_aily_skill(app, skill, batch_image, 'XL001', token)
            batch_image = []
            break
        time.sleep(3)
