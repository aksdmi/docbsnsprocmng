import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = 'Q123456q'
    ACCMNG_ADMIN = os.environ.get('ACCMNG_ADMIN')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = (os.environ.get('DEV_DATABASE_URL') or 
        'postgresql://postgres:postgres@127.0.0.1:54323/accmng')



config = {
    'development': DevelopmentConfig,

    'default': DevelopmentConfig
}
