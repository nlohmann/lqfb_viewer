# -*- coding: utf-8 -*-

#############################################################################
# LiquidFeedback Viewer - Bootstrap version
#
# Copyright (c) 2013 Niels Lohmann
# 
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the 'Software'),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
#############################################################################

import json
import os
import urllib
import urllib2

# everything for Flask
from flask import render_template, request, session, flash
from app import app, helper

from utils import api_load, api_load_all
import filter


###############
# INITIALIZER #
###############

def fix_path():
    """
    create a path prefix
    """
    if os.path.dirname(__file__) == "":
        return ""
    else:
        return os.path.dirname(__file__) + "/"

@app.before_first_request
def prepare():
    """
    preload certain information for convenience
    """

    # load settings
    settings_file = fix_path() + 'settings.json'
    print('+ loading settings from ' + settings_file + '...')
    helper['settings'] = json.load(open(settings_file))

    # load enums
    enums_file = fix_path() + 'enums.json'
    print('+ loading enums from ' + enums_file + '...')
    helper['enums'] = json.load(open(enums_file))

    # number of http requests
    helper['requests'] = 0

    # policies
    helper['policy'] = dict()
    data = api_load('/policy')
    for p in data['result']:
        helper['policy'][p['id']] = p['name']

    # unit
    helper['unit'] = dict()
    data = api_load('/unit')
    for p in data['result']:
        helper['unit'][p['id']] = p['name']

    # areas
    helper['area'] = dict()
    data = api_load('/area')
    for p in data['result']:
        helper['area'][p['id']] = p['name']

    helper['unit2area'] = dict()
    for p in data['result']:
        helper['unit2area'][p['id']] = p['unit_id']

    # info (only maximal row limit is interesting)
    data = api_load('/info')
    helper['result_row_limit_max'] = data['settings']['result_row_limit']['max']

    # initiatives
    helper['initiative'] = dict()
    data = api_load_all('/initiative')
    for p in data['result']:
        helper['initiative'][p['id']] = p['name']

    print "+ up and running..."

##############
# END POINTS #
##############

@app.route('/')
def show_index():
    data = api_load('/info', session)
    if not 'current_access_level' in session:
        flash('Deine neue Zugangsberechtigung ist: <i class="' + helper['enums']['access'][data['current_access_level']]['icon'] + '"></i> ' + helper['enums']['access'][data['current_access_level']]['name'] + '.', "info")
        
    session['current_access_level'] = data['current_access_level']
    return render_template('index.html', data=data, helper=helper)

@app.route('/regelwerke')
def show_policies():
    data = api_load('/policy')
    return render_template('policies.html', data=data, helper=helper)

@app.route('/regelwerke/<int:id>')
def show_policy(id):
    data = api_load('/policy?policy_id=' + str(id))
    return render_template('policy.html', data=data, helper=helper)

@app.route('/gliederungen')
def show_units():
    data = api_load('/unit')
    return render_template('units.html', data=data, helper=helper)

@app.route('/ereignisse')
def show_events():
    data = dict()
    data['event'] = api_load_all('/event')
    data['initiative'] = api_load_all('/initiative')
    data['issue'] = api_load_all('/issue')
    data['suggestion'] = api_load_all('/suggestion?rendered_content=html')
    return render_template('events.html', data=data, helper=helper)

@app.route('/themen')
def show_issues():
    data = api_load_all('/issue')
    return render_template('issues.html', data=data, helper=helper)

@app.route('/themen/<int:id>')
def show_issue(id):
    data = dict()
    data['issue'] = api_load('/issue?issue_id=' + str(id))
    data['initiative'] = api_load('/initiative?issue_id=' + str(id))
    data['policy'] = api_load('/policy?policy_id=' + str(data['issue']['result'][0]['policy_id']))
    return render_template('issue.html', data=data, helper=helper)

@app.route('/initiative/<int:id>')
def show_initiative(id):
    data = dict()
    data['initiative'] = api_load('/initiative?initiative_id=' + str(id))
    data['issue'] = api_load('/issue?issue_id=' + str(data['initiative']['result'][0]['issue_id']))
    data['current_draft'] = api_load('/draft?initiative_id=' + str(id) + '&current_draft=true&render_content=html')
    data['battle'] = api_load('/battle?issue_id=' + str(data['initiative']['result'][0]['issue_id']))

    return render_template('initiative.html', data=data, helper=helper)

@app.route('/mitglieder')
def show_members():
    data = dict()
    data['member'] = api_load('/member', session)
    return render_template('members.html', data=data, helper=helper)

@app.route('/themenbereiche')
def show_areas():
    data = api_load('/area')
    return render_template('areas.html', data=data, helper=helper)

@app.route('/themenbereiche/<int:id>')
def show_area(id):
    data = dict()
    data['area'] = api_load('/area?area_id=' + str(id))
    data['allowed_policy'] = api_load('/allowed_policy?area_id=' + str(id))
    return render_template('area.html', data=data, helper=helper)

@app.route('/mitglieder/<int:id>')
def show_member(id):
    data = dict()
    data['privilege'] = api_load('/privilege?member_id=' + str(id), session)
    data['membership'] = api_load('/membership?member_id=' + str(id), session)
    data['initiator'] = api_load('/initiator?member_id=' + str(id), session)
    data['delegation'] = api_load('/delegation?member_id=' + str(id), session)
    data['delegating_voter'] = api_load('/delegating_voter?member_id=' + str(id), session)
    data['voter'] = api_load('/voter?member_id=' + str(id) + '&formatting_engine=html', session)
    data['vote'] = api_load('/vote?member_id=' + str(id), session)
    data['event'] = api_load('/event')
    data['member'] = api_load('/member?member_id=' + str(id) + '&render_statement=html', session)
    data['member_image'] = api_load('/member_image?member_id=' + str(id), session)
    data['member_history'] = api_load('/member_history?member_id=' + str(id), session)
    return render_template('member.html', data=data, helper=helper)

@app.route('/einstellungen', methods=['GET', 'POST'])
def show_settings():
    # store the key
    if request.method == 'POST' and 'submit_key' in request.form:
        session.permanent = True
        session['api_key'] = request.form['api_key']

        # check the key
        url = helper['settings']['api_url'] + '/session'
        data = {'key': session['api_key']}
        rq = json.load(urllib2.urlopen(url, urllib.urlencode(data)))

        if rq['status'] == 'ok':
            flash(u"Dein API-Schlüssel wurde akzeptiert.", "success")
            session['session_key'] = rq['session_key']
        elif rq['status'] == 'forbidden':
            flash(u"Dein API-Schlüssel wurde nicht akzeptiert.", "error")
            if 'session_key' in session:
                session.pop('session_key')
        else:
            flash(u"Es gab ein Problem mit deinem API-Schlüssel: " + rq['error'], "error")
            if 'session_key' in session:
                session.pop('session_key')

        # get access level
        data = api_load('/info', session)
        session['current_access_level'] = data['current_access_level']
        flash('Deine neue Zugangsberechtigung ist: <i class="' + helper['enums']['access'][data['current_access_level']]['icon'] + '"></i> ' + helper['enums']['access'][data['current_access_level']]['name'] + '.', "info")


    # delete the key
    if request.method == 'POST' and 'delete_key' in request.form:
        flash(u"Der API-Schlüssel wurde gelöscht.", "success")
        if 'session_key' in session:
            session.pop('session_key')

        if 'api_key' in session:
            session.pop('api_key')

        # get access level
        data = api_load('/info', session)
        session['current_access_level'] = data['current_access_level']
        flash('Deine neue Zugangsberechtigung ist: <i class="' + helper['enums']['access'][data['current_access_level']]['icon'] + '"></i> ' + helper['enums']['access'][data['current_access_level']]['name'] + '.', "info")

    return render_template('settings.html', helper=helper, session=session)
