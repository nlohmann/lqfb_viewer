# -*- coding: utf-8 -*-

from flask import render_template
from app import app, celery
from emails import send_email

@celery.task
def add(x, y):
    print "add is executed"
    return 10


@celery.task
def c_send():
    send_email('[LQFB] E-Mail-Benachrichtigung', 'niels.lohmann@gmail.com', ['niels.lohmann@gmail.com'], 'foo', 'foo')
