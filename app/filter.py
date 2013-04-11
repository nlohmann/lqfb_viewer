# -*- coding: utf-8 -*-
from flask import session
from app import app, helper

from utils import cache_load

from math import ceil

from datetime import datetime
import pytz
import iso8601

# for German dates, time zones and ISO8601 translation
import locale
locale.setlocale(locale.LC_ALL, 'de_DE.UTF-8')


@app.template_filter('nicedate')
def nicedate_filter(s, format='%A, %x, %X Uhr', timeago=True):
    """
    filter to format dazes given in ISO8601
    """

    if not timeago:
        return iso8601.parse_date(s).astimezone(pytz.timezone('Europe/Berlin')).strftime(format)
    else:
        local_tz = pytz.timezone('Europe/Berlin')
        default = "eben gerade"
        now = datetime.utcnow().replace(tzinfo=local_tz)
        date = iso8601.parse_date(s).astimezone(local_tz)
        diff = now - date

        #verschiedene zeitperioden - woche, monat, jahre eingebaut, falls benoetigt
        periods = (
            (diff.days / 365, "Jahr", "Jahre"),
            (diff.days / 30, "Monat", "Monate"),
            (diff.days / 7, "Woche", "Wochen"),
            (diff.days, "Tag", "Tagen"),
            #TODO: Fix that m*therf***ing hack down here !!!
            (diff.seconds / 3600 + 2, "Stunde", "Stunden"),
            (diff.seconds / 60, "Minute", "Minuten"),
            (diff.seconds, "Sekunde", "Sekunden"),
        )
        #import locale
        #locale.setlocale(locale.LC_ALL, 'deutsch')
        dateFormatted = datetime.strftime(date, "%d.%m.%Y %H:%M:%S")
        for period, singular, plural in periods:

            if period:
                if diff.days == 1:
                    return '<span data-toggle="tooltip" title="%s">%s</span>' % (dateFormatted, "gestern")
                elif 1 < diff.days < 7:
                    return '<span data-toggle="tooltip" title="%s">%s</span>' % (dateFormatted, datetime.strftime(date, "%A"))
                elif diff.days > 6:
                    date = date
                    return u'<span data-toggle="tooltip" title="%s">%s</span>' % (dateFormatted, datetime.strftime(date, "%d. %B").decode('utf-8'))
                elif diff.days > 365:
                    return '<span data-toggle="tooltip" title="%s">%s</span>' % (dateFormatted, datetime.strftime(date, "%d.%m.%Y"))
                else:
                    return '<span data-toggle="tooltip" title="%s">vor %d %s</span>' % (dateFormatted, period, singular if period == 1 else plural)

        return default

@app.template_filter('member')
def member_filter(member_id, name=False):
    """
    never reveal names to unauthorized users
    """
    if not 'current_access_level' in session or session['current_access_level'] != 'member':
        return '<i class="icon-user"></i>&nbsp;Mitglied&nbsp;' + str(member_id)

    result = '<i class="icon-user"></i>&nbsp;<a href="/mitglieder/' + str(member_id) + '">'
    if name:
        data = cache_load('/member?member_id=' + str(member_id), session)
        if data['result'][0]['name'] != "":
            result += data['result'][0]['name']
        else:
            result += 'Mitglied&nbsp;' + str(member_id)
    else:
        result += 'Mitglied&nbsp;' + str(member_id)
    result += '</a>'
    return result

@app.template_filter('issue')
def issue_filter(issue_id):
    return '<i class="icon-list-alt"></i>&nbsp;<a href="/themen/' + str(issue_id) + '">Thema&nbsp;' + str(issue_id) + '</a>'

@app.template_filter('area')
def area_filter(area_id, title=False):
    result = '<i class="icon-columns"></i>&nbsp;'

    if title:
        result += helper['area'][area_id]
    else:
        result += 'Themnbereich&nbsp;' + str(area_id)
    return result

@app.template_filter('policy')
def policy_filter(policy_id, title=False):
    result = '<i class="icon-book"></i>&nbsp;'

    if title:
        result += helper['policy'][policy_id]
    else:
        result += 'Regelwerk&nbsp;' + str(policy_id)
    return result

@app.template_filter('unit')
def unit_filter(unit_id, title=False):
    result = '<i class="icon-sitemap"></i>&nbsp;'

    if title:
        result += helper['unit'][unit_id]
    else:
        result += 'Gliederung&nbsp;' + str(unit_id)
    return result

@app.template_filter('initiative')
def initiative_filter(initiative_id, title=False):
    result = '<i class="icon-file-alt"></i>&nbsp;<a href="/initiative/' + str(initiative_id) + '">'

    if title:
        result += helper['initiative'][initiative_id]
    else:
        result += 'Initiative&nbsp;' + str(initiative_id)
    result += '</a>'
    return result

@app.template_filter('quorum')
def quorum_filter(issue_id):
    """
    a filter to return the quorum of a given issue
    """
    data = dict()
    data['issue'] = cache_load('/issue?issue_id=' + str(issue_id))
    data['policy'] = cache_load('/policy?policy_id=' + str(data['issue']['result'][0]['policy_id']))
    return int(ceil((float(data['policy']['result'][0]['initiative_quorum_num']) / float(data['policy']['result'][0]['initiative_quorum_den'])) * data['issue']['result'][0]['population']))

@app.template_filter('is_url')
def is_url(url):
    """
    GANZ einfacher Test, ob es sich um eine URL handelt. Kann man mal mit nem RegEx aufbessern
    """
    return str(url).find('http')>-1 or str(url).find('https')>-1
