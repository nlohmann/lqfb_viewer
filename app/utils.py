# -*- coding: utf-8 -*-
from app import helper, cache, fob, app
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
        
        helper['requests'] += 1
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

# fob_store(data, 'issue_id', 'issue')
# fob['issue']['issue_id']
def fob_store(obj, key, name):
    fob[name] = dict()
    fob[name][key] = dict()
    for element in obj:
        fob[name][key][element[key]] = element

def fob_get(a, b, c):
    try:
        element = fob[a][b][c]
    except:
        fob_update()
        element = fob[a][b][c]
    return element

def fob_update():
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
    if 'result' in data:
        fob_store(data['result'], 'id', 'suggestion')
