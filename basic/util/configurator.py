import configparser

def get_aily_env():
    # 读取配置文件
    config = configparser.ConfigParser()
    config.read('config.ini', encoding='utf-8')
    # 应用id、secret
    app_id = config['aily']['app_id']
    app_secret = config['aily']['app_secret']
    # 表格token、table id
    base_token = config['base']['token']
    camera_table_id = config['base']['camera_table_id']
    record_table_id = config['base']['record_table_id']
    # aily的app、skill
    app = config['aily']['app']
    skill = config['aily']['skill']
    # 本地文件夹目录地址
    path = config['app']['path']

    return app_id, app_secret, base_token, camera_table_id, record_table_id, app, skill, path
