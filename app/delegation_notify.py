# -*- coding: utf-8 -*-
from app import helper, cache, app, models, db
from utils import api_load, api_load_all
import json
import urllib
import urllib2

def process_delegation_difference():
    def new_delegation(dele):
        result = "NEUE DELEGATION: Mitglied %d delegiert nun auf Mitglied %d" % (dele['truster_id'], dele['trustee_id'])
        return result

    def deleted_delegation(dele):
        result = "GELÖSCHTE DELEGATION: Mitglied %d delegiert nicht mehr auf Mitglied %d" % (dele['truster_id'], dele['trustee_id'])
        return result

    def changed_delgation(old, new):
        if old['truster_id'] != new['truster_id']:
            return "error"

        if new['trustee_id'] == None:
            return deleted_delegation(old)

        result = "GEÄNDERTE DELEGATION: Mitglied %d delegiert nun auf Mitglied %d (statt zuvor auf Mitglied %d)" % (old['truster_id'], new['trustee_id'], old['trustee_id'])
        return result
    
    added_delegations, removed_delegations = diff_delegations()

    if added_delegations == [] and removed_delegations == []:
        return
    
    for key, value in added_delegations.iteritems():
        if key in removed_delegations:
            print changed_delgation(removed_delegations[key], added_delegations[key])
        else:
            print new_delegation(added_delegations[key])

    for key, value in removed_delegations.iteritems():
        if not key in added_delegations:
            print removed_delegations(removed_delegations[key])


def diff_delegations():
    # get the members
    u = models.Member.query.all()
    if u == None:
        return {}, {}

    # get a session key
    url = app.config['LQFB_API'] + '/session'
    data = {'key': u[0].api_key}
    rq = json.load(urllib2.urlopen(url, urllib.urlencode(data)))

    # use the session key
    session = dict()
    session['session_key'] = rq['session_key']

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
