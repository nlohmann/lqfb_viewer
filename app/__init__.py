#############################################################################
# LiquidFeedback Viewer - Bootstrap version
#
# Copyright (c) 2013 Niels Lohmann
# 
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the 'Software'),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
#############################################################################

# everything for Flask
from flask import Flask
from werkzeug.contrib.cache import SimpleCache
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.mail import Mail

# Celery
from celery import Celery

###########
# GLOBALS #
###########

# the Flask app
app = Flask(__name__)
app.config.from_object('config')

# database
db = SQLAlchemy(app)

# Celery
celery = Celery('app.tasks')
celery.conf.update(app.config)

# email
mail = Mail(app)

# cache
cache = SimpleCache(threshold=30000, default_timeout=300)

# global dictionary for convenience data
helper = dict()

from app import server, models
