from os import environ


class Config(object):
    SECRET_KEY = environ.get('SECRET_KEY') or 'hard to guess it'

    SQLALCHEMY_DATABASE_URI = environ.get('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAIL_SERVER = environ.get('MAIL_SERVER')
    MAIL_PORT = environ.get('MAIL_PORT')
    MAIL_USE_TLS = True
    MAIL_USE_SSL = True
    MAIL_USERNAME = environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = environ.get('MAIL_PASSWORD')
    FLASKY_MAIL_SUBJECT_PREFIX = '[%s]' % environ.get('FLASKY_MAIL_SENDER')[:5]
    FLASKY_MAIL_SENDER = environ.get('FLASKY_MAIL_SENDER')
    FLASKY_MAIL_ADMIN = environ.get('FLASKY_MAIL_ADMIN')

    @staticmethod
    def init_app(app):
        pass


config = {'production': Config}
