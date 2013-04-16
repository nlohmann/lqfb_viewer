import os
basedir = os.path.abspath(os.path.dirname(__file__))

# debug mode
DEBUG = True

# secret key
SECRET_KEY = 'secret'

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
