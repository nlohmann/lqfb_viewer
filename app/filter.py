# -*- coding: utf-8 -*-
from flask import session
from jinja2._markupsafe import Markup
from app import app, helper, fob

from utils import api_load

from math import ceil

from datetime import datetime
import pytz
import iso8601

# for German dates, time zones and ISO8601 translation
import locale
try:
    locale.setlocale(locale.LC_ALL, 'de_DE.UTF-8')
except:
    pass


@app.template_filter('nicedate')
def nicedate_filter(_date, format='%A, %x, %X Uhr', timeago=True):
    if not timeago:
         return iso8601.parse_date(_date).astimezone(pytz.timezone('Europe/Berlin')).strftime(format)

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
def member_filter(member_id, link=False):
    # get name
    if not 'current_access_level' in session or session['current_access_level'] != 'member':
        result = "Mitglied&nbsp;" + str(member_id)
        # it does not make sense to link without member access level
        link = False
    else:
        data = api_load('/member', q={'member_id': member_id}, session=session)
        if data['result'][0]['name'] != "":
            result = data['result'][0]['name']
        else:
            result = 'Mitglied&nbsp;%d' % member_id

    # add link
    if link:
        result = '<a href="/mitglieder/' + str(member_id) + '">' + result + '</a>'

    # add icon
    return '<i class="icon-user"></i>&nbsp;' + result

@app.template_filter('issue')
def issue_filter(issue_id, link=False):
    # get "name"
    result = "Thema&nbsp;" + str(issue_id)

    # add link
    if link:
        result = '<a href="/themen/' + str(issue_id) + '">' + result + '</a>'

    # add icon
    return '<i class="icon-list-alt"></i>&nbsp;' + result

@app.template_filter('area')
def area_filter(area_id, link=False):
    # get name
    result = fob['area']['id'][area_id]['name']

    # add link
    if link:
        result = '<a href="/themenbereiche/' + str(area_id) + '">' + result + '</a>'

    # add icon
    return '<i class="icon-columns"></i>&nbsp;' + result

@app.template_filter('suggestion')
def suggestion_filter(suggestion_id):
    # get name
    result = fob['suggestion']['id'][suggestion_id]['name']

    # add icon
    return '<i class="icon-lightbulb"></i>&nbsp;' + result

@app.template_filter('policy')
def policy_filter(policy_id, link=False):
    # get name
    result = fob['policy']['id'][policy_id]['name']

    # add link
    if link:
        result = '<a href="/regelwerke/' + str(policy_id) + '">' + result + '</a>'

    # add icon
    return '<i class="icon-book"></i>&nbsp;' + result

@app.template_filter('unit')
def unit_filter(unit_id, link=False):
    # get name
    result = fob['unit']['id'][unit_id]['name']

    # add link
    if link:
        result = '<a href="/gliederungen/' + str(unit_id) + '">' + result + '</a>'

    # add icon
    return '<i class="icon-sitemap"></i>&nbsp;' + result

@app.template_filter('initiative')
def initiative_filter(initiative_id, link=False):
    # special case: status quo
    if initiative_id == None:
        return "Status Quo"
    
    # get name
    result = fob['initiative']['id'][initiative_id]['name']

    # add link
    if link:
        result = '<a href="/initiative/' + str(initiative_id) + '">' + result + '</a>'

    # add icon
    return '<i class="icon-file-alt"></i>&nbsp;' + result



@app.template_filter('quorum')
def quorum_filter(issue_id):
    """
    a filter to return the quorum of a given issue
    """
    issue = fob['issue']['id'][issue_id]
    policy = fob['policy']['id'][issue['policy_id']]

    return int(ceil((float(policy['initiative_quorum_num']) / float(policy['initiative_quorum_den'])) * issue['population']))

@app.template_filter('is_url')
def is_url_filter(url):
    """
    GANZ einfacher Test, ob es sich um eine URL handelt. Kann man mal mit nem RegEx aufbessern
    """
    return str(url).find('http') > -1 or str(url).find('https') > -1

@app.template_filter('vote')
def vote_filter(grade):
    if grade == 0:
        return '<span class="badge">%d</span>' % grade
    if grade > 0:
        return '<span class="badge badge-success">%d</span>' % grade
    if grade < 0:
        return '<span class="badge badge-important">%d</span>' % grade

@app.template_filter('delegation')
def delegation_filter(weight):
    return '<span class="label label-info"><i class="icon-plus"></i> %d</span>' % weight
