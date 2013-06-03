# -*- coding: utf-8 -*-
from flask import session
from markupsafe import Markup

from app import app, helper
from utils import api_load, db_load

from math import ceil
from datetime import datetime, timedelta
import pytz
import iso8601

from dateutil.relativedelta import relativedelta

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
def member_filter(member_id, link=False, icon=True):
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

    if result == None:
        result = 'Mitglied&nbsp;%d' % member_id

    # add link
    if link:
        result = '<a href="/mitglieder/' + str(member_id) + '">' + result + '</a>'

    # add icon
    if icon:
        result = '<i class="icon-user"></i>&nbsp;' + result

    return result

@app.template_filter('issue')
def issue_filter(issue_id, link=False, icon=True):
    # get "name"
    result = "Thema&nbsp;" + str(issue_id)

    # add link
    if link:
        result = '<a href="/themen/' + str(issue_id) + '">' + result + '</a>'

    # add icon
    if icon:
        result = '<i class="icon-list-alt"></i>&nbsp;' + result

    return result

@app.template_filter('area')
def area_filter(area_id, link=True, icon=True):
    # get name
    result = db_load('/area', q={'area_id': area_id})['result'][0]['name']

    # add link
    if link:
        result = '<a href="/themenbereiche/' + str(area_id) + '">' + result + '</a>'

    # add icon
    if icon:
        result = '<i class="icon-columns"></i>&nbsp;' + result

    return result

@app.template_filter('suggestion')
def suggestion_filter(suggestion_id, icon=True):
    # get name
    result = db_load('/suggestion', q={'suggestion_id': suggestion_id})['result'][0]['name']

    # add icon
    if icon:
        result = '<i class="icon-lightbulb"></i>&nbsp;' + result

    return result

@app.template_filter('policy')
def policy_filter(policy_id, link=True, icon=True):
    # get name
    result = db_load('/policy', q={'policy_id': policy_id})['result'][0]['name']

    # add link
    if link:
        result = '<a href="/regelwerke/' + str(policy_id) + '">' + result + '</a>'

    # add icon
    if icon:
        result = '<i class="icon-book"></i>&nbsp;' + result

    return result

@app.template_filter('unit')
def unit_filter(unit_id, link=False, icon=True):
    # get name
    result = db_load('/unit', q={'unit_id': unit_id})['result'][0]['name']

    # add link
    if link:
        result = '<a href="/gliederungen/' + str(unit_id) + '">' + result + '</a>'

    # add icon
    if icon:
        result = '<i class="icon-sitemap"></i>&nbsp;' + result

    return result

@app.template_filter('initiative')
def initiative_filter(initiative_id, link=False, icon=True):
    # special case: status quo
    if initiative_id == None:
        return "Status Quo"
    
    # get name
    result = db_load('/initiative', q={'initiative_id': initiative_id})['result'][0]['name']

    # add link
    if link:
        result = '<a href="/initiative/' + str(initiative_id) + '">' + result + '</a>'

    # add icon
    if icon:
        result = '<i class="icon-file-alt"></i>&nbsp;' + result

    return result

# Returns the size of the quorum of a given issue. It is calculated from the respective policy and the population of the issue.
@app.template_filter('quorum')
def quorum_filter(issue_id):
    """
    a filter to return the quorum of a given issue
    """
    issue = db_load('/issue', q={'issue_id': issue_id})['result'][0]
    policy = db_load('/policy', q={'policy_id': issue['policy_id']})['result'][0]

    return int(ceil((float(policy['initiative_quorum_num']) / float(policy['initiative_quorum_den'])) * issue['population']))


# A simple test whether a given string could be a linkable URL.
@app.template_filter('is_url')
def is_url_filter(url):
    """
    GANZ einfacher Test, ob es sich um eine URL handelt. Kann man mal mit nem RegEx aufbessern
    """
    return str(url).find('http') > -1 or str(url).find('https') > -1


# A filter to return a unified graphical representation of a vote with different colors for agreement, refusal, and absention.
@app.template_filter('vote')
def vote_filter(grade):
    if grade == 0:
        return '<span class="badge">%d</span>' % grade
    if grade > 0:
        return '<span class="badge badge-success">%d</span>' % grade
    if grade < 0:
        return '<span class="badge badge-important">%d</span>' % grade


# A filter to return a unified graphical representation of delegations. It simply adds a large + in front of a given integer.
@app.template_filter('delegation')
def delegation_filter(weight, icon=True):
    if weight > 0:
        if icon:
            return '<span class="label label-info"><i class="icon-plus"></i> %d</span>' % weight
        else:
            return '+%d' % weight
    else:
        return ''


# This filter creates percentages of the times of the four phases of a policy. These percentages can be used in a bar graph depciting the time phases. The script assumes a policy_id and the name of a phase is given. The result is a number between 0.0 and 100.0, though it is limited for each phase such that it does not exceed a certain factor.
@app.template_filter('policy_time_bars')
def policy_time_bars_filter(policy_id, phase):
    p = db_load('/policy', q={'policy_id': policy_id})['result'][0]
    result = dict()

    result['admission_time'] = 0
    if 'minutes' in p['admission_time']:
        result['admission_time'] += p['admission_time']['minutes']
    if 'hours' in p['admission_time']:
        result['admission_time'] += p['admission_time']['hours'] * 60
    if 'days' in p['admission_time']:
        result['admission_time'] += p['admission_time']['days'] * 60 * 24
    if 'years' in p['admission_time']:
        result['admission_time'] += p['admission_time']['years'] * 60 * 24 * 365

    result['discussion_time'] = 0
    if 'minutes' in p['discussion_time']:
        result['discussion_time'] += p['discussion_time']['minutes']
    if 'hours' in p['discussion_time']:
        result['discussion_time'] += p['discussion_time']['hours'] * 60
    if 'days' in p['discussion_time']:
        result['discussion_time'] += p['discussion_time']['days'] * 60 * 24
    if 'years' in p['discussion_time']:
        result['discussion_time'] += p['discussion_time']['years'] * 60 * 24 * 365

    result['verification_time'] = 0
    if 'minutes' in p['verification_time']:
        result['verification_time'] += p['verification_time']['minutes']
    if 'hours' in p['verification_time']:
        result['verification_time'] += p['verification_time']['hours'] * 60
    if 'days' in p['verification_time']:
        result['verification_time'] += p['verification_time']['days'] * 60 * 24
    if 'years' in p['verification_time']:
        result['verification_time'] += p['verification_time']['years'] * 60 * 24 * 365

    result['voting_time'] = 0
    if 'minutes' in p['voting_time']:
        result['voting_time'] += p['voting_time']['minutes']
    if 'hours' in p['voting_time']:
        result['voting_time'] += p['voting_time']['hours'] * 60
    if 'days' in p['voting_time']:
        result['voting_time'] += p['voting_time']['days'] * 60 * 24
    if 'years' in p['voting_time']:
        result['voting_time'] += p['voting_time']['years'] * 60 * 24 * 365

    # make sure no bar is way larger than all the others
    final = result

    factor = float(result['admission_time']) / float(result['discussion_time'] + result['verification_time'] + result['voting_time'])
    if factor > 20:
        final['admission_time'] = float(result['admission_time']) / (factor * 0.75)
        
    factor = float(result['discussion_time']) / float(result['admission_time'] + result['verification_time'] + result['voting_time'])
    if factor > 20:
        final['discussion_time'] = float(result['discussion_time']) / (factor * 0.75)

    factor =  float(result['verification_time']) / float(result['admission_time'] + result['discussion_time'] + result['voting_time'])
    if factor > 20:
        final['verification_time'] = float(result['verification_time']) / (factor * 0.75)

    factor =  float(result['voting_time']) / float(result['admission_time'] + result['discussion_time'] + result['verification_time'])
    if factor > 20:
        final['voting_time'] = float(result['voting_time']) / (factor * 0.75)

    total_time = final['admission_time'] + final['discussion_time'] + final['verification_time'] + final['voting_time']

    return (final[phase] / float(total_time)) * 100.0


# A filter to return the length of a policy's phase.
@app.template_filter('policy_time')
def policy_time_filter(policy_id, phase):
    p = db_load('/policy', q={'policy_id': policy_id})['result'][0]

    if 'minutes' in p[phase]:
        return "%d Minuten" % p[phase]['minutes'] if p[phase]['minutes'] != 1 else "%d Minute" % p[phase]['minutes']
    if 'hours' in p[phase]:
        return "%d Stunden" % p[phase]['hours'] if p[phase]['hours'] != 1 else "%d Stunde" % p[phase]['hours']
    if 'days' in p[phase]:
        return "%d Tage" % p[phase]['days'] if p[phase]['days'] != 1 else "%d Tag" % p[phase]['days']
    if 'years' in p[phase]:
        return "%d Jahre" % p[phase]['years'] if p[phase]['years'] != 1 else "%d Jahr" % p[phase]['years']


# A filter to calculate a date in the future given am offset as JSON timestamp as specified in http://dev.liquidfeedback.org/trac/lf/wiki/API and a base date given in ISO8601. The result is an ISO8601 representation of the base date with the offset added.
@app.template_filter('future_date')
def future_date_filter(_base, _offset):
    thisdate = iso8601.parse_date(_base).astimezone(pytz.timezone('Europe/Berlin'))
    result = thisdate
    if 'minutes' in _offset:
        result += relativedelta(minutes = +_offset['minutes'])
    if 'hours' in _offset:
        result += relativedelta(hours = +_offset['hours'])
    if 'days' in _offset:
        result += relativedelta(days = +_offset['days'])
    if 'years' in _offset:
        result += relativedelta(years = +_offset['years'])

    return result.isoformat()


# A filter to calculate the end of a given phase of a policy.
@app.template_filter('end_of_phase')
def end_of_phase_filter(policy_id, phase):
    p = db_load('/policy', q={'policy_id': policy_id})['result'][0]
    thisdate=datetime.now(tz=pytz.timezone('Europe/Berlin'))

    end_of = dict()
    end_of['admission_time']    = future_date_filter(thisdate.isoformat(), p['admission_time'])
    end_of['discussion_time']   = future_date_filter(end_of['admission_time'], p['discussion_time'])
    end_of['verification_time'] = future_date_filter(end_of['discussion_time'], p['verification_time'])
    end_of['voting_time']       = future_date_filter(end_of['verification_time'], p['voting_time'])

    return end_of[phase]


# The following functions are taken from https://github.com/imtapps/django-pretty-times/blob/master/pretty_times/pretty.py to have a nicer (relative) representation of times in the past and future.
@app.template_filter('mynicedate')
def mynicedate_filter(_date, interval=False, coarse=True):
    def _pretty_format(diff_amount, units, text, past):
        pretty_time = (diff_amount + units / 2) / units
        if past:
            return "vor %d %s" % (pretty_time, text)
        else:
            return "in %d %s" % (pretty_time, text)

    def get_small_increments(seconds, past):
        if seconds < 10:
            result = 'gerade jetzt'
        elif seconds < 60:
            result = _pretty_format(seconds, 1, 'Sekunden', past)
        elif seconds < 120:
            result = past and 'vor einer Minute' or 'in einer Minute'
        elif seconds < 3600:
            result = _pretty_format(seconds, 60, 'Minuten', past)
        elif seconds < 7200:
            result = past and 'vor einer Stunde' or 'in einer Stunde'
        else:
            result = _pretty_format(seconds, 3600, 'Stunden', past)
        return result

    def get_large_increments(now, then):
        if then > now:
            past = False
            diff = then - now
        else:
            past = True
            diff = now - then

        days = diff.days

        # fix: timedelta is too coarse: if it is 22:00, and some event is "in 5 hours" (meaning it's 3:00 on the next day), then timedelta would report "in 0 days", which is wrong. So we calculate the hours of now and then and add a day if their sum is >= 24.
        if not past:
            if now.hour + diff.seconds/3600 >= 24:
                days = days + 1

        if days == 0:
            result = 'heute'
        elif days == 1:
            result = past and 'gestern' or 'morgen'
        elif days == 2:
            result = past and 'vorgestern' or u'übermorgen'
        elif days < 7:
            result = _pretty_format(days, 1, 'Tagen', past)
        elif days < 14:
            result = past and 'letzte Woche' or 'kommende Woche'
        elif days < 31:
            result = _pretty_format(days, 7, 'Wochen', past)
        elif days < 61:
            if then.month != now.month:
                result = past and 'letzter Monat' or 'kommender Monat'
            else:
                result = _pretty_format(days, 7, 'Wochen', past)
        elif days < 365:
            result = _pretty_format(days, 30, 'Monaten', past)
        elif days < 730:
            if then.year != now.year:
                result = past and 'letztes Jahr' or 'kommendes Jahr'
            else:
                result = _pretty_format(days, 30, 'Monaten', past)
        else:
            result = _pretty_format(days, 365, 'Jahren', past)
        return result

    def get_large_interval(days):
        if days == 1:
            result = 'bis morgen'
        elif days < 7:
            result = str(days) + ' Tage'
        elif days < 14:
            result = 'eine Woche'
        elif days < 31:
            result = str((days + 7 / 2) / 7) + ' Wochen'
        elif days < 61:
            result = 'ein Monat'
        elif days < 365:
            result = str((days + 30 / 2) / 30) + ' Monate'
        elif days < 730:
            result = 'ein Jahr'
        else:
            result = str((days + 365 / 2) / 365) + ' Monate'
        return result

    def get_small_interval(seconds):
        if seconds < 10:
            result = 'bis gleich'
        elif seconds < 60:
            result = str((seconds + 1 / 2) / 1) + ' Sekunden'
        elif seconds < 120:
            result = 'eine Minute'
        elif seconds < 3600:
            result = str((seconds + 60 / 2) / 60) + ' Minuten'
        elif seconds < 7200:
            result = 'eine Stunde'
        else:
            result = str((seconds + 3600 / 2) / 3600) + ' Stunden'
        return result

    then = iso8601.parse_date(_date).astimezone(pytz.timezone('Europe/Berlin'))
    now = datetime.now(then.tzinfo)

    if then > now:
        past = False
        diff = then - now
    else:
        past = True
        diff = now - then

    humandatestring = ""

    if diff.days is 0 and not coarse:
        if interval:
            humandatestring = get_small_interval(diff.seconds)
        else:
            humandatestring = get_small_increments(diff.seconds, past)
    else:
        if interval:
            humandatestring = get_large_interval(diff.days)
        else:
            humandatestring = get_large_increments(now, then)

    return Markup('<span data-toggle="tooltip" title="%s">%s</span>' % (then.strftime('%A, %x, %H:%M Uhr'), humandatestring))
