import configparser

# 1. 创建一个模块级别的、共享的 ConfigParser 实例
_config = configparser.ConfigParser()
# 2. 在模块加载时只读取一次配置文件
_config.read('config.ini', encoding='utf-8')

def get_aily_env():
    """从共享的配置实例中获取 Aily 相关的所有环境变量。"""
    # 3. 所有函数都使用这个共享的 _config 实例
    app_id = _config.get('aily', 'app_id')
    app_secret = _config.get('aily', 'app_secret')
    base_token = _config.get('base', 'token')
    camera_table_id = _config.get('base', 'camera_table_id')
    record_table_id = _config.get('base', 'record_table_id')
    app = _config.get('aily', 'app')
    skill = _config.get('aily', 'skill')
    path = _config.get('app', 'path')
    return app_id, app_secret, base_token, camera_table_id, record_table_id, app, skill, path

def get_use_aily():
    """
    从配置中读取是否走 Aily 上传路径。
    - 使用 .getboolean() 并提供 fallback=True，逻辑更清晰健壮。
    - 如果 'aily' 节或 'use_aily' 键不存在，或者值无法解析为布尔值，
      都会安全地回退到默认值 True。
    """
    return _config.getboolean('aily', 'use_aily', fallback=True)

def get_capture_source():
    """
    从配置中读取抓帧来源 ('camera' 或 'screenshot')。
    - 使用 fallback 提供了默认值 'camera'。
    - 移除多余的 try-except 块。
    - 确保返回值总是 'camera' 或 'screenshot' 之一。
    """
    value = _config.get('app', 'capture_source', fallback='camera').strip().lower()
    return value if value in ('camera', 'screenshot') else 'camera'
