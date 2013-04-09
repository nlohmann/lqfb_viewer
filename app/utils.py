# -*- coding: utf-8 -*-
from app import helper, cache
from flask import flash
import urllib2,json
#############
# FUNCTIONS #
#############

def cache_load(url, session=None):
    """
    cached loading of JSON objects: we use the URL as key
    """
    url_copy = url

    if session != None:
        if 'session_key' in session:
            if url.find('?') != -1:
                seperator = '&'
            else:
                seperator = '?'
            url = url + seperator + "session_key=" + session['session_key']

    url = helper['settings']['api_url'] + url
    rv = cache.get(url)
    if rv is None:
        print '+ requesting ' + url_copy
        helper['requests'] += 1
        res = urllib2.urlopen(url).read()

        if res == '"Invalid session key"':
            if session != None:
                if 'session_key' in session:
                    session.pop('session_key')
                flash("Deine Session ist abgelaufen.", "error")
                return cache_load(url_copy)

        rv = json.loads(res)

        if rv['status'] == 'forbidden':
            flash("Zugriff verweigert.", "error")

        cache.set(url, rv, timeout=5 * 60)
    return rv


def get_all(url):
    """
    collect all results by repeated calls with offsets
    """
    offset = 0
    limit = helper['result_row_limit_max']
    result = dict()

    if url.find('?') != -1:
        seperator = '&'
    else:
        seperator = '?'

    while True:
        obj = cache_load(url + seperator + 'limit=' + str(limit) + '&offset=' + str(offset))
        offset = offset + limit

        if len(result) == 0:
            result = obj
        else:
            result['result'] = result['result'] + obj['result']

        if len(obj['result']) < limit:
            return result

