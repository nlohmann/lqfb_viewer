# -*- coding: utf-8 -*-
from app import helper, cache, app, models, db
from flask import flash
import urllib, urllib2, json

#############
# FUNCTIONS #
#############

def api_load(endpoint, q=None, session=None, forceLoad=False):
    original_q = q

    if q is None:
        q = {}

    # if session is given, add session key to parameters
    if session != None and 'session_key' in session:
        q['session_key'] = session['session_key']

    # build url from endpoint and parameters
    url = app.config['LQFB_API'] + endpoint
    if q != {}:
        url += '?' + urllib.urlencode(q)

    # try to use cache
    rv = cache.get(url)

    if rv is None or forceLoad == True:
        print ">", endpoint
        
        res = urllib2.urlopen(url).read()

        if res == '"Invalid session key"':
            if session != None and 'session_key' in session:
                session.pop('session_key')
            flash("Deine Session ist abgelaufen.", "error")
            return api_load(endpoint=endpoint, q=original_q, forceLoad=forceLoad)

        rv = json.loads(res)

        cache.set(url, rv)
    return rv

def api_load_all(endpoint, q=None, session=None, forceLoad=False):
    if q is None:
        q = {}

    q['offset'] = 0
    q['limit'] = helper['result_row_limit_max']
    result = dict()
    
    while True:
        obj = api_load(endpoint, q=q, session=session, forceLoad=forceLoad)
        q['offset'] += q['limit']

        if len(result) == 0:
            result = obj
        else:
            result['result'] = result['result'] + obj['result']

        if not 'result' in obj or len(obj['result']) < q['limit']:
            return result

def fob_store(objects, endpoint):
    for element in objects:
        u = models.APIData.query.get((element['id'], endpoint))
        if u == None:
            u = models.APIData(id=element['id'], endpoint=endpoint, payload=json.dumps(element))
            db.session.add(u)
        else:
            u.endpoint=endpoint

    db.session.commit()

def fob_get(endpoint, id):
    u = models.APIData.query.get((id, endpoint))

    if u == None:
        fob_update()
        u = models.APIData.query.get((id, endpoint))

    return json.loads(u.payload)

def fob_update():
    # info (only maximal row limit is interesting)
    data = api_load('/info')
    helper['result_row_limit_max'] = data['settings']['result_row_limit']['max']

    # policies
    data = api_load('/policy')
    fob_store(data['result'], 'policy')

    # unit
    data = api_load('/unit')
    fob_store(data['result'], 'unit')

    # areas
    data = api_load('/area')
    fob_store(data['result'], 'area')

    # issues
    data = api_load_all('/issue')
    fob_store(data['result'], 'issue')

    # initiatives
    data = api_load_all('/initiative')
    fob_store(data['result'], 'initiative')

    # suggestions
    data = api_load_all('/suggestion')
    fob_store(data['result'], 'suggestion')
