class Config(object):
    DEBUG = False
    TESTING = False

    SESSION_COOKIE_SECURE = True
class ProductionConfig(Config):
    pass

class DevelopmentConfig(Config):
    DEBUG = True
    SESSION_COOKIE_SECURE = False

class TestingConfig(Config):
    TESTING = True

    SESSION_COOKIE_SECURE = False