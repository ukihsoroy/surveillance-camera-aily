from aily.aily_requests import *
from screen.camera_screen import *
from screen.screenshot_full import *

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

    while True:
        #截取屏幕
        # file_name = fullscreen(path)

        #链接IP，截取视频帧数
        file_name = camera_screen(ip, path)

        #获取token
        token = get_tenant_token(app_id, app_secret)

        # 上传文件
        file_id = upload_file(token, file_name)

        # 调用aily技能
        run_aily_skill(app, skill, file_id, 'XL001', token)

        # 等待60秒继续
        time.sleep(60)

