# -*- coding: utf-8 -*-
from app import helper, cache, app, models, db
from flask import flash
import urllib, urllib2, json

#################
# API-INTERFACE #
#################

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
        status = "> " + endpoint
        if q != {}:
            status += ' (query)'
        if forceLoad:
            status += " !"
        if session != None:
            status = ">" + status
        print status
        #print url

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
    result['result'] = list()
    
    while True:
        obj = api_load(endpoint, q=q, session=session, forceLoad=forceLoad)
        q['offset'] += q['limit']

        if len(result) == 0:
            result = obj
        else:
            result['result'] = result['result'] + obj['result']

        if not 'result' in obj or len(obj['result']) < q['limit']:
            return result


################
# DB-INTERFACE #
################

def db_load(endpoint, q=None):
    # strip the slash from the endpoint
    endpoint = endpoint[1:]

    # make sure the query is a dict
    if q is None:
        q = {}

    # make sure we only answer for endpoints that are stored in the database
    if not endpoint in ['unit', 'policy', 'area', 'event', 'initiative', 'draft', 'suggestion', 'initiative', 'issue']:
        return None

    # use primary key if possible
    if endpoint + '_id' in q:
        # in case the query contains 'area_id=x' for the endpoint '/area', query the database for (endpoint='area', id=x)
        id = q[endpoint + '_id']
        rows = models.APIData.query.filter_by(id=id, endpoint=endpoint).all()
        # remove the entry from the query for future checks
        del q[endpoint + '_id']
    else:
        rows = models.APIData.query.filter_by(endpoint=endpoint).all()

    # put the result into a dict for compatibility reasons
    result = dict()
    result['result'] = list()

    # filter elements according to query
    for row in rows:
        element = json.loads(row.payload)
        keep_element = True

        # drop element if query is not fulfilled
        for key in q.iterkeys():
            if element[key] != q[key]:
                keep_element = False

        if keep_element:
            result['result'].append(element)

    return result


#################
# FOB-INTERFACE #
#################

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


##############
# DB-UPDATES #
##############

def regular_update():
    # These information are seldomly updated, and new data cannot be detected any other way than by a regular forced update. This function should be called each time the server is started, and periodically every hour.
    
    # info (only maximal row limit is interesting)
    data = api_load('/info')
    helper['result_row_limit_max'] = data['settings']['result_row_limit']['max']

    # unit
    data = api_load('/unit')
    fob_store(data['result'], 'unit')

    # policies
    data = api_load('/policy')
    fob_store(data['result'], 'policy')

    # areas
    data = api_load('/area')
    fob_store(data['result'], 'area')

    print '[] regular DB update complete'

def cascaded_update():
    # info (only maximal row limit is interesting)
    data = api_load('/info')
    helper['result_row_limit_max'] = data['settings']['result_row_limit']['max']

    # get all events
    events = api_load_all('/event')

    # get stored last id
    u = models.Timestamp.query.get("event")
    if u == None:
        last_id = None
        new_last_id = 0
    else:
        last_id = u.id
        new_last_id = last_id

    # collect all events that need processing
    todo_events = list()
    for event in events['result']:
        if last_id == None or event['id'] > last_id:
            todo_events.append(event)
            if event['id'] > new_last_id:
                new_last_id = event['id']

    # update db with new last id
    if u == None:
        u = models.Timestamp(id = new_last_id, endpoint="event")
        db.session.add(u)
    else:
        u.id = new_last_id
    db.session.commit()

    # store new events
    fob_store(todo_events, 'event')

    # collect issues and initiatives that have changed
    todo_issues = set()
    todo_initiatives = set()

    for event in todo_events:
        if 'issue_id' in event and event['issue_id'] != None:
            todo_issues.add(event['issue_id'])
        if 'initiative_id' in event and event['initiative_id'] != None:
            todo_initiatives.add(event['initiative_id'])

    # query and store new issues
    if len(todo_issues) > 0:
        data = api_load('/issue', q={'issue_id': ",".join(str(x) for x in todo_issues)})
        fob_store(data['result'], 'issue')

    # query and store new initiatives, drafts, and suggestions
    if len(todo_initiatives) > 0:
        data = api_load('/initiative', q={'initiative_id': ",".join(str(x) for x in todo_initiatives)})
        fob_store(data['result'], 'initiative')
        data = api_load('/draft', q={'initiative_id': ",".join(str(x) for x in todo_initiatives), 'render_content': 'html'})
        fob_store(data['result'], 'draft')
        data = api_load('/suggestion', q={'initiative_id': ",".join(str(x) for x in todo_initiatives), 'rendered_content': 'html'})
        fob_store(data['result'], 'suggestion')

    print '[] processed ', len(todo_events), 'new events'


def fob_update():
    # info (only maximal row limit is interesting)
    data = api_load('/info')
    helper['result_row_limit_max'] = data['settings']['result_row_limit']['max']

    # update unit, area, and policy
    regular_update()

    # update the rest
    cascaded_update()

    # issues
    data = api_load_all('/issue')
    fob_store(data['result'], 'issue')

    # initiatives
    data = api_load_all('/initiative')
    fob_store(data['result'], 'initiative')

    # suggestions
    data = api_load_all('/suggestion', q={'rendered_content': 'html'})
    fob_store(data['result'], 'suggestion')

    # events
    data = api_load_all('/event')
    fob_store(data['result'], 'event')
