# -*- coding: utf-8 -*-

import json
import os
import urllib
import urllib2

# everything for Flask
from flask import render_template, request, Response, session, flash, abort
from app import app, helper, models, db
from emails import send_email
from utils import api_load, api_load_all, fob_update, db_load
from ical import create_ical
from aggregators import issue_aggregated

# Wochenschau
from datetime import datetime, date, timedelta
import iso8601


###############
# INITIALIZER #
###############

@app.before_first_request
def prepare():
    """
    preload certain information for convenience
    """

    def fix_path():
        """
        create a path prefix
        """
        if os.path.dirname(__file__) == "":
            return ""
        else:
            return os.path.dirname(__file__) + "/"

    # load enums
    enums_file = fix_path() + 'enums.json'
    print('+ loading enums from ' + enums_file + '...')
    helper['enums'] = json.load(open(enums_file))

    # initialize the FOB
    #fob_update()

    # register the db_load function for Jinja templates
    app.jinja_env.globals.update(db_load=db_load)

    print "[] up and running..."

##############
# END POINTS #
##############

@app.route('/')
def show_index():
    data = api_load('/info', session=session)
    if session == None or not 'current_access_level' in session:
        flash('Deine neue Zugangsberechtigung ist: <i class="' + helper['enums']['access'][data['current_access_level']]['icon'] + '"></i> ' + helper['enums']['access'][data['current_access_level']]['name'] + '.', 'info')

    session['current_access_level'] = data['current_access_level']
    return render_template('index.html', data=data, helper=helper, ourl='index/index.html')

@app.route('/regelwerke')
def show_policies():
    data = db_load('/policy')
    return render_template('policies.html', data=data, helper=helper, ourl='policy/list.html')

@app.route('/regelwerke/<int:policy_id>')
def show_policy(policy_id):
    data = db_load('/policy', q={'policy_id': policy_id})
    return render_template('policy.html', data=data, helper=helper, ourl='policy/show/%d.html' % policy_id)

@app.route('/gliederungen')
def show_units():
    data = db_load('/unit')
    return render_template('units.html', data=data, helper=helper, ourl='index/index.html?filter_unit=global')

@app.route('/gliederungen/<int:unit_id>')
def show_unit(unit_id):
    data = dict()
    data['unit'] = db_load('/unit', q={'unit_id': unit_id})

    data['privilege'] = api_load('/privilege', q={'unit_id': unit_id}, session=session)

    return render_template('unit.html', data=data, helper=helper, ourl='unit/show/%d.html' % unit_id)

@app.route('/ereignisse')
def show_events():
    data = dict()
    data['event'] = db_load('/event')
    data['initiative'] = db_load('/initiative')
    data['issue'] = db_load('/issue')
    data['suggestion'] = db_load('/suggestion')
    return render_template('events.html', data=data, helper=helper, ourl='index/index.html?tab=timeline&filter_unit=global')

@app.route('/themen')
def show_issues():
    data = db_load('/issue')
    return render_template('issues.html', data=data, helper=helper)

@app.route('/themen/<int:issue_id>')
def show_issue(issue_id):
    data = issue_aggregated(issue_id=issue_id, session=session)
    return render_template('issue.html', data=data, helper=helper, ourl='issue/show/%d.html' % issue_id)

@app.route('/initiative/<int:initiative_id>')
def show_initiative(initiative_id):
    data = dict()
    data['initiative'] = db_load('/initiative', q={'initiative_id': initiative_id})
    data['issue'] = db_load('/issue', q={'issue_id': data['initiative']['result'][0]['issue_id']})
    data['draft'] = db_load('/draft', q={'initiative_id': initiative_id})
    data['suggestion'] = db_load('/suggestion', q={'initiative_id': initiative_id})
    data['battle'] = api_load('/battle', q={'issue_id': data['initiative']['result'][0]['issue_id']})

    data['initiator'] = api_load('/initiator', q={'initiative_id': initiative_id}, session=session)

    return render_template('initiative.html', data=data, helper=helper, ourl='initiative/show/%d.html' % initiative_id)

@app.route('/themenbereiche')
def show_areas():
    data = db_load('/area')
    return render_template('areas.html', data=data, helper=helper)

@app.route('/themenbereiche/<int:area_id>')
def show_area(area_id):
    data = dict()
    data['area'] = db_load('/area', q={'area_id': area_id})
    data['allowed_policy'] = api_load('/allowed_policy', q={'area_id': area_id})
    return render_template('area.html', data=data, helper=helper, ourl='area/show/%d.html' % area_id)

@app.route('/mitglieder')
def show_members():
    data = dict()
    data['member'] = api_load('/member', session=session)
    return render_template('members.html', data=data, helper=helper, ourl='index/index.html?tab=members')

@app.route('/mitglieder/<int:member_id>')
def show_member(member_id):
    if 'current_access_level' not in session or session['current_access_level'] != 'member':
        abort(403)

    data = dict()
    data['event'] = db_load('/event')

    data['privilege'] = api_load('/privilege', q={'member_id': member_id}, session=session)
    data['membership'] = api_load('/membership', q={'member_id': member_id}, session=session)
    data['initiator'] = api_load('/initiator', q={'member_id': member_id}, session=session)
    data['delegation_in'] = api_load('/delegation', q={'member_id': member_id, 'direction': 'in'}, session=session)
    data['delegation_out'] = api_load('/delegation', q={'member_id': member_id, 'direction': 'out'}, session=session)
    data['delegating_voter'] = api_load('/delegating_voter', q={'member_id': member_id}, session=session)
    data['voter'] = api_load('/voter', q={'member_id': member_id, 'formatting_engine': 'html'}, session=session)
    data['vote'] = api_load('/vote', q={'member_id': member_id}, session=session)
    data['interest'] = api_load('/interest', q={'member_id': member_id, 'snapshot': 'latest'}, session=session)
    data['member'] = api_load('/member', q={'member_id': member_id, 'render_statement': 'html'}, session=session)
    data['member_image'] = api_load('/member_image', q={'member_id': member_id}, session=session)
    data['member_history'] = api_load('/member_history', q={'member_id': member_id}, session=session)

    return render_template('member.html', data=data, helper=helper, ourl='member/show/%d.html' % member_id)

@app.route('/einstellungen', methods=['GET', 'POST'])
def show_settings():
    # store the key
    if request.method == 'POST' and 'submit_key' in request.form:
        session.permanent = True
        session['api_key'] = request.form['api_key']

        # check the key
        url = app.config['LQFB_API'] + '/session'
        data = {'key': session['api_key']}
        rq = json.load(urllib2.urlopen(url, urllib.urlencode(data)))

        if rq['status'] == 'ok':
            flash(u"Dein API-Schlüssel wurde akzeptiert und verschlüsselt im Cookie gespeichert.", "success")
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
        flash('Deine neue Zugangsberechtigung ist: <i class="' + helper['enums']['access'][data['current_access_level']]['icon'] + '"></i> ' + helper['enums']['access'][data['current_access_level']]['name'] + '.', 'info')

        # get my member id
        if 'current_member_id' in data:
            session['current_member_id'] = data['current_member_id']

            # take care of the email address
            u = models.Member.query.get(session['current_member_id'])
            if u != None:
                session['email'] = u.email
        else:
            if 'current_member_id' in session:
                session.pop('current_member_id')

    # delete the key
    if request.method == 'POST' and 'delete_key' in request.form:
        session.clear()
        flash(u"Der API-Schlüssel wurde aus dem Cookie gelöscht.", "success")

        # get access level
        data = api_load('/info', session=session, forceLoad=True)
        session['current_access_level'] = data['current_access_level']
        flash('Deine neue Zugangsberechtigung ist: <i class="' + helper['enums']['access'][data['current_access_level']]['icon'] + '"></i> ' + helper['enums']['access'][data['current_access_level']]['name'] + '.', 'info')

    # store the email (and the API key)
    if request.method == 'POST' and 'submit_email' in request.form:
        if 'current_access_level' not in session or session['current_access_level'] != 'member':
            abort(403)
        
        session['email'] = request.form['email']
        u = models.Member.query.get(session['current_member_id'])
        if u == None:
            u = models.Member(member_id=session['current_member_id'], email=request.form['email'], api_key=session['api_key'], active=True)
            db.session.add(u)
            flash('E-Mail-Adresse gespeichert.', 'info')
        else:
            u.email = request.form['email']
            flash('E-Mail-Adresse aktualisert.', 'info')
        db.session.commit()
        send_email('[LQFB] E-Mail-Benachrichtigung', app.config['ADMINS'][0], [session['email']], render_template('welcome_email.txt'), render_template('welcome_email.html'))

    if request.method == 'POST' and 'delete_email' in request.form:
        if 'current_access_level' not in session or session['current_access_level'] != 'member':
            abort(403)

        if 'email' in session:
            session.pop('email')
        u = models.Member.query.get(session['current_member_id'])
        if u != None:
            db.session.delete(u)
            db.session.commit()
        flash(u'E-Mail-Adresse gelöscht.', 'info')

    # now display the page
    return render_template('settings.html', helper=helper, session=session)

@app.route('/kalender.ics')
def show_ical():
    return Response(create_ical(), mimetype='text/calendar')

@app.route('/wochenschau')
def show_wochenschau():
    week_ago = datetime.now()-timedelta(days=7)
    data = dict()
    data['monday'] = week_ago.isoformat()
    data['week_number'] = week_ago.isocalendar()[1] + 1
    data['closed']  = api_load_all('/issue', q={'issue_closed_after': week_ago.isoformat()})
    data['created'] = api_load_all('/issue', q={'issue_created_after': week_ago.isoformat()})
    data['frozen']  = api_load_all('/issue', q={'issue_half_frozen_after': week_ago.isoformat()})
    data['voting']  = api_load_all('/issue', q={'issue_state': 'voting'})
    return render_template('wochenschau.html', data=data, helper=helper)

@app.route('/statistiken')
def show_statistiken():
    data = dict()
    data['issue'] = api_load_all('/issue', q={'unit_id': 1})
    data['unit'] = db_load('/unit')
    return render_template('stats.html', data=data, helper=helper)


#######
# API #
#######

@app.route('/api/issue/<int:issue_id>')
def api_issue(issue_id):
    res = json.dumps(issue_aggregated(issue_id=issue_id, session=session), sort_keys=True, indent=4)
    return Response(res, mimetype='application/json')
