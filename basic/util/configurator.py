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

def get_use_aily():
    """从配置中读取是否走 Aily 上传（默认 True）"""
    config = configparser.ConfigParser()
    config.read('config.ini', encoding='utf-8')
    # 若不存在该键，默认 True 以保持原有行为
    try:
        return config.getboolean('aily', 'use_aily')
    except Exception:
        return True

def get_capture_source():
    """从配置中读取抓帧来源：'camera' 或 'screenshot'，默认 'camera'"""
    config = configparser.ConfigParser()
    config.read('config.ini', encoding='utf-8')
    try:
        value = config.get('app', 'capture_source', fallback='camera').strip().lower()
        return value if value in ('camera', 'screenshot') else 'camera'
    except Exception:
        return 'camera'
