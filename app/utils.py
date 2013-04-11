# -*- coding: utf-8 -*-
from app import helper, cache
from flask import flash
import urllib, urllib2, json

#############
# FUNCTIONS #
#############

def api_load(endpoint, params={}, session=None):
    """
    cached loading of JSON objects: we use the URL as key
    """

    # if session is given, add session key to parameters
    if session != None and 'session_key' in session:
        params['session_key'] = session['session_key']

    # build url from endpoint and parameters
    url = helper['settings']['api_url'] + endpoint
    if params != {}:
        url += '?' + urllib.urlencode(params)

    # try to use cache
    rv = cache.get(url)

    # if not found, request
    if rv is None:
        print '> requesting ' + endpoint
        helper['requests'] += 1
        res = urllib2.urlopen(url).read()

        # if session key is invalid, discard it and retry
        if res == '"Invalid session key"':
            session.pop('session_key')
            flash("Deine Session ist abgelaufen.", "error")
            return api_load(endpoint, params, session)

        rv = json.loads(res)

        if rv['status'] == 'forbidden':
            flash("Zugriff verweigert.", "error")

        # cache object
        cache.set(url, rv, timeout=5 * 60)

    return rv


def api_loadAll(endpoint, params={}, session=None):
    """
    cached loading of all elements given an API endpoint
    """
    
    # add offset and limit to parameters
    params['offset'] = 0
    params['limit'] = helper['result_row_limit_max']

    result = dict()

    while True:
        # get data with current offset
        obj = api_load(endpoint, params, session)

        # increase offset
        params['offset'] += params['limit']

        # combine result arrays
        if len(result) == 0:
            result = obj
        else:
            result['result'] = result['result'] + obj['result']

        # return if we get an array with length below the limit
        if len(obj['result']) < params['limit']:
            return result
