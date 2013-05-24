# -*- coding: utf-8 -*-
from app import helper, cache, app, models, db
from utils import api_load, api_load_all
from emails import send_email
from flask import render_template, session
import json
import urllib
import urllib2

def delegation_notify(notifications, session):
    ctx = app.test_request_context()
    ctx.push()
    send_email('[LQFB] Delegationen', app.config['ADMINS'][0], ['niels.lohmann@piraten-mv.de'],
        render_template('delegations_email.txt', notifications=notifications),
        render_template('delegations_email.html', notifications=notifications))

def process_delegation_difference():
    def getSession():
        # get the members
        u = models.Member.query.all()
        if u == []:
            return

        # get a session key
        url = app.config['LQFB_API'] + '/session'
        data = {'key': u[0].api_key}
        rq = json.load(urllib2.urlopen(url, urllib.urlencode(data)))

        # use the session key
        session = dict()
        session['session_key'] = rq['session_key']
        return session

    session = getSession()
    if session == None:
        return

    added_delegations, removed_delegations = get_delegation_diff(session)

    if added_delegations == {} and removed_delegations == {}:
        return

    notifications = dict()
    notifications['new'] = list()
    notifications['removed'] = list()
    notifications['changed'] = list()

    for key, value in added_delegations.iteritems():
        if key in removed_delegations:
            if added_delegations[key]['trustee_id'] == None:
                notifications['removed'].append(removed_delegations[key])
            else:
                if removed_delegations[key]['trustee_id'] == None:
                    notifications['new'].append(added_delegations[key])
                else:
                    notifications['changed'].append((removed_delegations[key], added_delegations[key]))
        else:
            notifications['new'].append(added_delegations[key])

    for key, value in removed_delegations.iteritems():
        if not key in added_delegations:
            notifications['removed'].append(removed_delegations[key])

    delegation_notify(notifications, session)

def get_delegation_diff(session):
    # get current delegations
    current_delegation = api_load('/delegation', session=session)
    current_delegation = current_delegation['result']

    # get past delegations
    u = models.KeyValue.query.get('delegation')

    # update database
    if u == None:
        # bootstrapping: if database is empty, store current delegations and return
        u = models.KeyValue(key='delegation', value=json.dumps(current_delegation))
        db.session.add(u)
        db.session.commit()
        return {}, {}
    else:
        past_delegation = json.loads(u.value)
        u.value=json.dumps(current_delegation)
        db.session.commit()

    # collect differences
    added_delegations = dict()
    removed_delegations = dict()

    for x in current_delegation:
        if not x in past_delegation:
            added_delegations[x['id']] = x

    for x in past_delegation:
        if not x in current_delegation:
            removed_delegations[x['id']] = x

    return added_delegations, removed_delegations
