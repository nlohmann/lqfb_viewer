# -*- coding: utf-8 -*-

from app import app, celery
from utils import cascaded_update, regular_update
from delegation_notify import process_delegation_difference
from celery.task.schedules import crontab
from celery.decorators import periodic_task

@periodic_task(run_every=crontab(minute='*/1'))
def c_cascaded_update():
    e = cascaded_update()
    return str(e)

@periodic_task(run_every=crontab(minute='*/5'))
def c_regular_update():
    e = regular_update()
    return str(e)

@periodic_task(run_every=crontab(minute='*/1'))
def c_delegation_notification():
    process_delegation_difference()
