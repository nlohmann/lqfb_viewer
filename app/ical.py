# -*- coding: utf-8 -*-

from icalendar import Calendar, Event
from app import app, helper
from utils import api_load, api_load_all
import pytz
from datetime import datetime
from filter import future_date_filter, policy_filter, area_filter
import iso8601

# Return a calendar with one event for each issue that is currently in voting phase.
def create_ical():
    data = dict()
    data['voting']  = api_load_all('/issue', q={'issue_state': 'voting'})

    tz = pytz.timezone('Europe/Berlin')

    cal = Calendar()
    cal.add('prodid', '-//Niels Lohmann//LiquidFeedback Viewer//DE')
    cal.add('version', '2.0')

    for issue in data['voting']['result']:
        start_time = iso8601.parse_date(issue['fully_frozen']).astimezone(pytz.timezone('Europe/Berlin'))
        end_time = iso8601.parse_date(future_date_filter(issue['fully_frozen'], issue['voting_time'])).astimezone(pytz.timezone('Europe/Berlin'))

        event = Event()
        event.add('summary', u'Abstimmung %s %d' % (policy_filter(issue['policy_id'], False, False), issue['id']))
        event.add('description', u'Abstimmung über Thema %d im Themenbereich "%s" mit Regelwerk %s.' % (issue['id'], area_filter(issue['area_id'], False, False), policy_filter(issue['policy_id'], False, False) ))
        event.add('location', u'%s' % (area_filter(issue['area_id'], False, False)))
        event.add('url', '%s/issue/show/%d.html' % (app.config['LQFB_URL'], issue['id']))
        event.add('dtstart', start_time)
        event.add('dtend', end_time)
        event.add('dtstamp', datetime.now(tz=tz))
        event['uid'] = '%s/issue/show/%d.html' % (app.config['LQFB_URL'], issue['id'])
        event.add('priority', 5)
        cal.add_component(event)
    
    return cal.to_ical()
