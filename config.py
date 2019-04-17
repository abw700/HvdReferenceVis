import os

# base directory
basedir = os.path.abspath(os.path.dirname(__file__))


# Config for all environments
class Config(object):
    '''common config'''
    DB_CONFIG = {
        'endpoints': 'rv-harvard-capstone-db.c5usqplnbvhe.us-east-1.rds.amazonaws.com',
        'dbname': 'rvcapsrv1',
        'username': 'rvcap',
        'password': 'rWJ5is53',
        'pool_recycle': 3600
    }
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://' + DB_CONFIG['username'] + ':' + DB_CONFIG['password'] + '@' + DB_CONFIG['endpoints'] + '/' + DB_CONFIG['dbname'] + '?charset=utf8mb4'


# Dev environment config
class DevelopmentConfig(Config):
    '''dev config'''
    DEBUG = True
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'rvcapsrv1.db')


# Staging environment config
class StagingConfig(Config):
    '''stage config'''
    DEBUG = True
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:rWJ5is53@0.0.0.0/rvcapsrv1?charset=utf8mb4'


# Test environment config
class TestConfig(Config):
    '''test config'''
    DEBUG = False


# Prod environment config
class ProductionConfig(Config):
    '''prod config'''
    DEBUG = False


# Select app config
app_config = {
    'development': DevelopmentConfig,
    'stage': StagingConfig,
    'test': TestConfig,
    'production': ProductionConfig,
}

