import configparser
import os

def get_aily_env():
    config = configparser.ConfigParser()
    config.read('config.ini', encoding='utf-8')
    app_id = os.environ.get('AILY_APP_ID', config['aily']['app_id'])
    app_secret = os.environ.get('AILY_APP_SECRET', config['aily']['app_secret'])
    base_token = os.environ.get('AILY_BASE_TOKEN', config['base']['token'])
    table_id = os.environ.get('AILY_TABLE_ID', config['base']['table_id'])
    app = os.environ.get('AILY_APP', config['aily']['app'])
    skill = os.environ.get('AILY_SKILL', config['aily']['skill'])
    path = os.environ.get('AILY_PATH', config['app']['path'])
    return app_id, app_secret, base_token, table_id, app, skill, path
