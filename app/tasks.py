# -*- coding: utf-8 -*-

from app import app, celery
from utils import cascaded_update, regular_update

@celery.task
def c_cascaded_update():
    cascaded_update()

@celery.task
def c_regular_update():
    regular_update()
