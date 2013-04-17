# -*- coding: utf-8 -*-
from app import helper, cache, fob, app
from flask import flash
import urllib, urllib2, json

#############
# FUNCTIONS #
#############

def api_load(endpoint, q=None, session=None, forceLoad=False):
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
            session.pop('session_key')
            flash("Deine Session ist abgelaufen.", "error")
            return api_load(endpoint, params, session)

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

        if len(obj['result']) < q['limit']:
            return result

# fob_store(data, 'issue_id', 'issue')
# fob['issue']['issue_id']
def fob_store(obj, key, name):
    fob[name] = dict()
    fob[name][key] = dict()
    for element in obj:
        fob[name][key][element[key]] = element
