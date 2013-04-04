#!/usr/bin/env python

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
import urllib2

# everything for Flask
from flask import Flask
from flask import render_template
from werkzeug.contrib.cache import SimpleCache

# for German dates, time zones and ISO8601 translation
import locale
import pytz
import iso8601
locale.setlocale(locale.LC_ALL, 'de_DE.UTF-8')


###########
# GLOBALS #
###########

# the Flask app
app = Flask(__name__)

# global dictionary for convenience data
helper = dict()

# cache
cache = SimpleCache()


#############
# FUNCTIONS #
#############

# cached loading of JSON objects: we use the URL as key
def cache_load(url):
    url = helper['settings']['api_url'] + url
    rv = cache.get(url)
    if rv is None:
        print '+ fetching ' + url
        rv = json.load(urllib2.urlopen(url))
        cache.set(url, rv, timeout=5 * 60)
    return rv


# preload ceartain information for convenience
def prepare():
    print('loading settings...')
    settings = json.load(open('settings.json'))
    helper['settings'] = settings

    # policies
    helper['policy'] = dict()
    data = cache_load('/policy')
    for p in data['result']:
        helper['policy'][p['id']] = p['name']

    # unit
    helper['unit'] = dict()
    data = cache_load('/unit')
    for p in data['result']:
        helper['unit'][p['id']] = p['name']

    # areas
    helper['area'] = dict()
    data = cache_load('/area')
    for p in data['result']:
        helper['area'][p['id']] = p['name']

    helper['unit2area'] = dict()
    for p in data['result']:
        helper['unit2area'][p['id']] = p['unit_id']

    # info (only maximal row limit is interesting)
    data = cache_load('/info')
    helper['result_row_limit_max'] = data['settings']['result_row_limit']['max']


# collect all results by repeated calls with offsets
def get_all(url):
    offset = 0
    limit = helper['result_row_limit_max']
    result = dict()

    while True:
        obj = cache_load(url + '?limit=' + str(limit) + '&offset=' + str(offset))
        offset = offset + limit
        
        if len(result) == 0:
            result = obj
        else:
            result['result'] = result['result'] + obj['result']
        
        if len(obj['result']) < limit:
            return result


###########
# FILTERS #
###########

# filter to format dazes given in ISO8601
@app.template_filter('nicedate')
def nicedate_filter(s, format='%A, %x, %X Uhr'):
    return iso8601.parse_date(s).astimezone(pytz.timezone('Europe/Berlin')).strftime(format)


##############
# END POINTS #
##############

@app.route('/')
def show_index():
    data = cache_load('/info')
    return render_template('index.html', data=data, helper=helper)

@app.route('/regelwerke')
def show_policies():
    data = cache_load('/policy')
    return render_template('policies.html', data=data)

@app.route('/regelwerke/<int:id>')
def show_policy(id):
    data = cache_load('/policy?policy_id=' + str(id))
    return render_template('policy.html', data=data, helper=helper)

@app.route('/gliederungen')
def show_units():
    data = cache_load('/unit')
    return render_template('units.html', data=data)

@app.route('/themen')
def show_issues():
    data = get_all('/issue')
    return render_template('issues.html', data=data, helper=helper)

@app.route('/themen/<int:id>')
def show_issue(id):
    data = dict()
    data['issue'] = cache_load('/issue?issue_id=' + str(id))
    data['initiative'] = cache_load('/initiative?issue_id=' + str(id))
    data['policy'] = cache_load('/policy?policy_id=' + str(data['issue']['result'][0]['policy_id']))
    return render_template('issue.html', data=data, helper=helper)

@app.route('/initiative/<int:id>')
def show_initiative(id):
    data = dict()
    data['initiative'] = cache_load('/initiative?initiative_id=' + str(id))
    data['issue'] = cache_load('/issue?issue_id=' + str(data['initiative']['result'][0]['issue_id']))
    data['current_draft'] = cache_load('/draft?initiative_id=' + str(id) + '&current_draft=true&render_content=html')
    data['battle'] = cache_load('/battle?issue_id=' + str(data['initiative']['result'][0]['issue_id']))

    return render_template('initiative.html', data=data, helper=helper)


####################
# START THE SERVER #
####################

prepare()

# let's go
if __name__ == '__main__':
    app.run()
