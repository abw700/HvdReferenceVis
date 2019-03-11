## Setup configuration for app and db


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

# Staging environment config
class StagingConfig(Config):
    '''stage config'''
    DEBUG = True
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False

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
    'production': ProductionConfig,
    'test': TestConfig,
    'stage': StagingConfig
}

