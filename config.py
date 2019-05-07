import os

# base directory
basedir = os.path.abspath(os.path.dirname(__file__))

# Config for all environments
class Config(object):
    '''common config'''
    DB_CONFIG = {
        'endpoints': os.environ.get('DB_ENDPOINTS', None),
        'dbname': os.environ.get('DB_DBNAME', None),
        'username': os.environ.get('DB_USERNAME', None),
        'password': os.environ.get('DB_PASS', None),
        'pool_recycle': 3600
    }
    for k,v in DB_CONFIG.items():
        if v is None:
            raise ValueError('Environment variable is missing for ' + k)
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://' + DB_CONFIG['username'] + ':' + DB_CONFIG['password'] + '@' + DB_CONFIG['endpoints'] + '/' + DB_CONFIG['dbname'] + '?charset=utf8mb4'
    CORS_HEADERS = 'Content-Type'
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False    

# Dev environment config -- Use local MySQL
class DevelopmentConfig(Config):
    '''dev config'''
    DEBUG = True

# Test environment config -- Use production database
class TestConfig(Config):
    '''test config'''
    DEBUG = True

# Prod environment config -- Use production database
class ProductionConfig(Config):
    '''prod config'''
    DEBUG = False

# Select app config
app_config = {
    'development': DevelopmentConfig,
    'test': TestConfig,
    'production': ProductionConfig,
}
