# -*- coding: utf-8 -*-
from flask import session
from jinja2._markupsafe import Markup
from app import app, helper

from utils import api_load

from math import ceil

from datetime import datetime
import pytz
import iso8601

# for German dates, time zones and ISO8601 translation
import locale
locale.setlocale(locale.LC_ALL, 'de_DE.UTF-8')


@app.template_filter('nicedate')
def nicedate_filter(s, format='%A, %x, %X Uhr', timeago=True):
    # """
    # filter to format dazes given in ISO8601
    # """
    #
    # if not timeago:
    #     return iso8601.parse_date(s).astimezone(pytz.timezone('Europe/Berlin')).strftime(format)
    # else:
    #     local_tz = pytz.timezone('Europe/Berlin')
    #     default = "eben gerade"
    #     now = datetime.utcnow().replace(tzinfo=local_tz)
    #     date = iso8601.parse_date(s).astimezone(local_tz)
    #     diff = now - date
    #
    #     #verschiedene zeitperioden - woche, monat, jahre eingebaut, falls benoetigt
    #     periods = (
    #         (diff.days / 365, "Jahr", "Jahre"),
    #         (diff.days / 30, "Monat", "Monate"),
    #         (diff.days / 7, "Woche", "Wochen"),
    #         (diff.days, "Tag", "Tagen"),
    #         #TODO: Fix that m*therf***ing hack down here !!!
    #         (diff.seconds / 3600 + 2, "Stunde", "Stunden"),
    #         (diff.seconds / 60, "Minute", "Minuten"),
    #         (diff.seconds, "Sekunde", "Sekunden"),
    #     )
    #     #import locale
    #     #locale.setlocale(locale.LC_ALL, 'deutsch')
    #     dateFormatted = datetime.strftime(date, "%d.%m.%Y %H:%M:%S")
    #     for period, singular, plural in periods:
    #
    #         if period:
    #             if diff.days == 1:
    #                 return '<span data-toggle="tooltip" title="%s">%s</span>' % (dateFormatted, "gestern")
    #             elif 1 < diff.days < 7:
    #                 return '<span data-toggle="tooltip" title="%s">%s</span>' % (dateFormatted, datetime.strftime(date, "%A"))
    #             elif diff.days > 6:
    #                 date = date
    #                 return u'<span data-toggle="tooltip" title="%s">%s</span>' % (dateFormatted, datetime.strftime(date, "%d. %B").decode('utf-8'))
    #             elif diff.days > 365:
    #                 return '<span data-toggle="tooltip" title="%s">%s</span>' % (dateFormatted, datetime.strftime(date, "%d.%m.%Y"))
    #             else:
    #                 return '<span data-toggle="tooltip" title="%s">vor %d %s</span>' % (dateFormatted, period, singular if period == 1 else plural)
    #
    #     return default
    return humandate(s,format,False)


def humandate(_date,format, timeago=True):

    thisdate = iso8601.parse_date(_date).astimezone(pytz.timezone('Europe/Berlin'))
    now = datetime.now(tz=pytz.timezone('Europe/Berlin'))
    delta = now - thisdate
    is_year = (now.year == thisdate.year)
    is_week = (thisdate.strftime('%W%Y') == now.strftime('%W%Y'))
    is_today = (now.day == thisdate.day and now.month == thisdate.month and is_year)

    if delta.seconds < 300:
        humandatestring = "gerade eben"
    elif delta.seconds < 3600:
        humandatestring = "%s Minuten" % (delta.seconds/60)
    elif (delta.seconds > 3600) and is_today:
        humandatestring = "%s Stunden" % (delta.seconds/(60*60))
    elif (delta.days < 2 ) and not is_today:
        humandatestring = "gestern"
    elif is_week:
        humandatestring = thisdate.strftime('%A')
    elif is_year:
        humandatestring = thisdate.strftime('%d. %B').decode('utf-8')
    else:
        humandatestring = thisdate.strftime('%d. %B %Y').decode('utf-8')

    return Markup('<span data-toggle="tooltip" title="%s">%s</span>' % (thisdate.strftime('%A, %x, %H:%M Uhr') ,humandatestring))



@app.template_filter('avatar')
def avatar_filter(member_id):
    if not 'current_access_level' in session or session['current_access_level'] != 'member':
        return '<i class="icon-user"></i>'
    
    data = api_load('/member_image', q={'member_id': member_id, 'type': 'avatar'}, session=session)
    if data['result'] != []:
        return '<img class="img-rounded" src="data:' + data['result'][0]['content_type'] + ';base64,' + data['result'][0]['data'] + '"/>'
    else:
        return '<i class="icon-user"></i>'

@app.template_filter('member')
def member_filter(member_id, name=False):
    """
    never reveal names to unauthorized users
    """
    if not 'current_access_level' in session or session['current_access_level'] != 'member':
        return '<i class="icon-user"></i>&nbsp;Mitglied&nbsp;%d' % member_id

    result = '<i class="icon-user"></i>&nbsp;<a href="/mitglieder/%d">' % member_id
    if name:
        data = api_load('/member', q={'member_id': member_id}, session=session)
        if data['result'][0]['name'] != "":
            result += data['result'][0]['name']
        else:
            result += 'Mitglied&nbsp;%d' % member_id
    else:
        result += 'Mitglied&nbsp;%d' % member_id
    result += '</a>'
    return result

@app.template_filter('issue')
def issue_filter(issue_id):
    return '<i class="icon-list-alt"></i>&nbsp;<a href="/themen/%d">Thema&nbsp;%d</a>' % (issue_id, issue_id)

@app.template_filter('area')
def area_filter(area_id, title=False):
    result = '<i class="icon-columns"></i>&nbsp;'

    if title:
        result += helper['area'][area_id]
    else:
        result += 'Themnbereich&nbsp;%d' % area_id
    return result

@app.template_filter('policy')
def policy_filter(policy_id, title=False):
    result = '<i class="icon-book"></i>&nbsp;'

    if title:
        result += helper['policy'][policy_id]
    else:
        result += 'Regelwerk&nbsp;%d' % policy_id
    return result

@app.template_filter('unit')
def unit_filter(unit_id, title=False):
    result = '<i class="icon-sitemap"></i>&nbsp;'

    if title:
        result += helper['unit'][unit_id]
    else:
        result += 'Gliederung&nbsp;%d' % unit_id
    return result

@app.template_filter('initiative')
def initiative_filter(initiative_id, title=False):
    result = '<i class="icon-file-alt"></i>&nbsp;<a href="/initiative/%d">' % initiative_id

    if title:
        result += helper['initiative'][initiative_id]
    else:
        result += 'Initiative&nbsp;%d' % initiative_id
    result += '</a>'
    return result

@app.template_filter('quorum')
def quorum_filter(issue_id):
    """
    a filter to return the quorum of a given issue
    """
    data = dict()
    data['issue'] = api_load('/issue', q={'issue_id': issue_id})
    data['policy'] = api_load('/policy', q={'policy_id': data['issue']['result'][0]['policy_id']})
    return int(ceil((float(data['policy']['result'][0]['initiative_quorum_num']) / float(data['policy']['result'][0]['initiative_quorum_den'])) * data['issue']['result'][0]['population']))

@app.template_filter('is_url')
def is_url(url):
    """
    GANZ einfacher Test, ob es sich um eine URL handelt. Kann man mal mit nem RegEx aufbessern
    """
    return str(url).find('http')>-1 or str(url).find('https')>-1
