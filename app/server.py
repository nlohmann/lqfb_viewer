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
from app import app, helper, fob

from utils import api_load, api_load_all, fob_store
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

    # info (only maximal row limit is interesting)
    data = api_load('/info')
    helper['result_row_limit_max'] = data['settings']['result_row_limit']['max']

    # policies
    data = api_load('/policy')
    fob_store(data['result'], 'id', 'policy')

    # unit
    data = api_load('/unit')
    fob_store(data['result'], 'id', 'unit')

    # areas
    data = api_load('/area')
    fob_store(data['result'], 'id', 'area')

    # issues
    data = api_load_all('/issue')
    fob_store(data['result'], 'id', 'issue')

    # initiatives
    data = api_load_all('/initiative')
    fob_store(data['result'], 'id', 'initiative')

    # suggestions
    data = api_load_all('/suggestion')
    fob_store(data['result'], 'id', 'suggestion')

    print "+ up and running..."

##############
# END POINTS #
##############

@app.route('/')
def show_index():
    data = api_load('/info', session=session)
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
    data = api_load('/policy', q={'policy_id': id})
    return render_template('policy.html', data=data, helper=helper)

@app.route('/gliederungen')
def show_units():
    data = api_load('/unit')
    return render_template('units.html', data=data, helper=helper)

@app.route('/gliederungen/<int:id>')
def show_unit(id):
    data = api_load('/unit', q={'unit_id': id})
    return render_template('unit.html', data=data, helper=helper)

@app.route('/ereignisse')
def show_events():
    data = dict()
    data['event'] = api_load_all('/event')
    data['initiative'] = api_load_all('/initiative')
    data['issue'] = api_load_all('/issue')
    data['suggestion'] = api_load_all('/suggestion', q={'rendered_content': 'html'})
    return render_template('events.html', data=data, helper=helper)

@app.route('/themen')
def show_issues():
    data = api_load_all('/issue')
    return render_template('issues.html', data=data, helper=helper, fob=fob)

@app.route('/themen/<int:id>')
def show_issue(id):
    data = dict()
    data['issue'] = api_load('/issue', q={'issue_id': id})
    data['initiative'] = api_load('/initiative', q={'issue_id': id})
    data['policy'] = api_load('/policy', q={'policy_id': data['issue']['result'][0]['policy_id']})
    data['interest'] = dict()
    data['interest']['latest'] = api_load('/interest', q={'issue_id': id, 'snapshot': 'latest'}, session=session)
    data['interest']['end_of_admission'] = api_load('/interest', q={'issue_id': id, 'snapshot': 'end_of_admission'}, session=session)
    data['interest']['half_freeze'] = api_load('/interest', q={'issue_id': id, 'snapshot': 'half_freeze'}, session=session)
    data['interest']['full_freeze'] = api_load('/interest', q={'issue_id': id, 'snapshot': 'full_freeze'}, session=session)
    return render_template('issue.html', data=data, helper=helper, fob=fob)

@app.route('/initiative/<int:id>')
def show_initiative(id):
    data = dict()
    data['initiative'] = api_load('/initiative', q={'initiative_id': id})
    data['issue'] = api_load('/issue', q={'issue_id': data['initiative']['result'][0]['issue_id']})
    data['battle'] = api_load('/battle', q={'issue_id': data['initiative']['result'][0]['issue_id']})
    data['draft'] = api_load('/draft', q={'initiative_id': id, 'render_content': 'html'})
    data['suggestion'] = api_load('/suggestion', q={'initiative_id': id})
    data['initiator'] = api_load('/initiator', q={'initiative_id': id}, session=session)

    return render_template('initiative.html', data=data, helper=helper)

@app.route('/mitglieder')
def show_members():
    data = dict()
    data['member'] = api_load('/member', session=session)
    return render_template('members.html', data=data, helper=helper)

@app.route('/themenbereiche')
def show_areas():
    data = api_load('/area')
    return render_template('areas.html', data=data, helper=helper)

@app.route('/themenbereiche/<int:id>')
def show_area(id):
    data = dict()
    data['area'] = api_load('/area', q={'area_id': id})
    data['allowed_policy'] = api_load('/allowed_policy', q={'area_id': id})
    return render_template('area.html', data=data, helper=helper)

@app.route('/mitglieder/<int:id>')
def show_member(id):
    data = dict()
    data['privilege'] = api_load('/privilege', q={'member_id': id}, session=session)
    data['membership'] = api_load('/membership', q={'member_id': id}, session=session)
    data['initiator'] = api_load('/initiator', q={'member_id': id}, session=session)
    data['delegation'] = api_load('/delegation', q={'member_id': id}, session=session)
    data['delegating_voter'] = api_load('/delegating_voter', q={'member_id': id}, session=session)
    data['voter'] = api_load('/voter', q={'member_id': id, 'formatting_engine': 'html'}, session=session)
    data['vote'] = api_load('/vote', q={'member_id': id}, session=session)
    data['event'] = api_load('/event')
    data['member'] = api_load('/member', q={'member_id': id, 'render_statement': 'html'}, session=session)
    data['member_image'] = api_load('/member_image', q={'member_id': id}, session=session)
    data['member_history'] = api_load('/member_history', q={'member_id': id}, session=session)
    return render_template('member.html', data=data, helper=helper, fob=fob)

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
        data = api_load('/info', session=session, forceLoad=True)
        session['current_access_level'] = data['current_access_level']
        flash('Deine neue Zugangsberechtigung ist: <i class="' + helper['enums']['access'][data['current_access_level']]['icon'] + '"></i> ' + helper['enums']['access'][data['current_access_level']]['name'] + '.', "info")

        # get my membet id
        if 'current_member_id' in data:
            session['current_member_id'] = data['current_member_id']
        else:
            if 'current_member_id' in session:
                session.pop('current_member_id')

    # delete the key
    if request.method == 'POST' and 'delete_key' in request.form:
        session.clear()
        flash(u"Der API-Schlüssel wurde gelöscht.", "success")

        # get access level
        data = api_load('/info', session=session, forceLoad=True)
        session['current_access_level'] = data['current_access_level']
        flash('Deine neue Zugangsberechtigung ist: <i class="' + helper['enums']['access'][data['current_access_level']]['icon'] + '"></i> ' + helper['enums']['access'][data['current_access_level']]['name'] + '.', "info")

    return render_template('settings.html', helper=helper, session=session)
