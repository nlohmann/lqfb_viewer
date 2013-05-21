# -*- coding: utf-8 -*-

from flask import render_template
from app import app, celery
from emails import send_email
from utils import fob_update

@celery.task
def c_send():
    send_email('[LQFB] E-Mail-Benachrichtigung', 'niels.lohmann@gmail.com', ['niels.lohmann@gmail.com'], 'foo', 'foo')

@celery.task
def c_update_db():
    fob_update()
