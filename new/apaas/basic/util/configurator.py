import configparser
import os

def get_aily_env():
    # apaas版本不需要使用aily的配置，此函数保留以保持兼容性
    raise NotImplementedError("This function is not implemented in Apaas version")


def get_apaas_env():
    # 读取配置文件
    config = configparser.ConfigParser()
    # 获取当前文件所在目录的父目录，即项目根目录
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    config_path = os.path.join(base_dir, 'config.ini')
    config.read(config_path, encoding='utf-8')
    # 本地文件夹目录地址
    path = config['app']['path']

    # apaas的client id、secret
    client_id = config['apaas']['client_id']
    client_secret = config['apaas']['client_secret']
    namespace = config['apaas']['namespace']

    return path, client_id, client_secret, namespace
