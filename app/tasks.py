# -*- coding: utf-8 -*-

from app import app, celery
from utils import cascaded_update, regular_update

@celery.task
def c_cascaded_update():
    e = cascaded_update()
    return str(e)

@celery.task
def c_regular_update():
    e = regular_update()
    return str(e)
