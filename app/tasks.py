# -*- coding: utf-8 -*-

from app import app, celery
from utils import cascaded_update, regular_update
from delegation_notify import process_delegation_difference

@celery.task
def c_cascaded_update():
    e = cascaded_update()
    return str(e)

@celery.task
def c_regular_update():
    e = regular_update()
    return str(e)

@celery.task
def c_delegation_notification():
    process_delegation_difference()
