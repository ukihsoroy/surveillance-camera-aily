import configparser
import os

def get_aily_env():
    # 读取配置文件
    config = configparser.ConfigParser()
    # 获取当前文件所在目录的父目录，即项目根目录
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    config_path = os.path.join(base_dir, 'config.ini')
    config.read(config_path, encoding='utf-8')
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

    return app_id, app_secret, base_token, table_id, app, skill, path


def get_apaas_env():
    # aily版本不需要使用apaas的配置，此函数保留以保持兼容性
    raise NotImplementedError("This function is not implemented in Aily version")
