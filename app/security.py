DEBUG = False
SECRET_KEY = 'hard to guess string'
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:123456@localhost:3306/movie'
SQLALCHEMY_TRACK_MODIFICATIONS = True
SQLALCHEMY_COMMIT_ON_TEARDOWN = True

# email
MAIL_SERVER = 'smtp.qq.com'
MAIL_PORT = 465
MAIL_USE_SSL = True
MAIL_USE_TSL = False
MAIL_USERNAME = 'admin@qq.com'
MAIL_PASSWORD = '123456'

try:
    from .local_security import *
except:
    pass
