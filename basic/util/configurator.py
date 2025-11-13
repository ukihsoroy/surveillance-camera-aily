import configparser
import os

def get_aily_env():
    config = configparser.ConfigParser()
<<<<<<< HEAD
    config.read('config.ini', encoding='utf-8')
    app_id = os.environ.get('AILY_APP_ID', config['aily']['app_id'])
    app_secret = os.environ.get('AILY_APP_SECRET', config['aily']['app_secret'])
    base_token = os.environ.get('AILY_BASE_TOKEN', config['base']['token'])
    table_id = os.environ.get('AILY_TABLE_ID', config['base']['table_id'])
    app = os.environ.get('AILY_APP', config['aily']['app'])
    skill = os.environ.get('AILY_SKILL', config['aily']['skill'])
    path = os.environ.get('AILY_PATH', config['app']['path'])
    return app_id, app_secret, base_token, table_id, app, skill, path
=======
    config.read('/Users/bytedance/Documents/GitHub/surveillance-camera-aily/config.ini', encoding='utf-8')
    # 应用id、secret
    app_id = config['aily']['app_id']
    app_secret = config['aily']['app_secret']
    # 表格token、table id
    base_token = config['base']['token']
    table_id = config['base']['table_id']
    # aily的app、skill
    app = config['aily']['app']
    skill = config['aily']['skill']
    # 本地文件夹目录地址
    path = config['app']['path']

    # apaas的client id、secret
    client_id = config['apaas']['client_id']
    client_secret = config['apaas']['client_secret']

    return app_id, app_secret, base_token, table_id, app, skill, path, client_id, client_secret


def get_apaas_env():
    # 读取配置文件
    config = configparser.ConfigParser()
    config.read('/Users/bytedance/Documents/GitHub/surveillance-camera-aily/config.ini', encoding='utf-8')
    # 本地文件夹目录地址
    path = config['app']['path']

    # apaas的client id、secret
    client_id = config['apaas']['client_id']
    client_secret = config['apaas']['client_secret']
    namespace = config['apaas']['namespace']

    return path, client_id, client_secret, namespace
>>>>>>> 307f84535c27207804a683b62afb26ead0a9a003
