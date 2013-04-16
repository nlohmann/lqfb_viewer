#!flask/bin/python
# -*- coding: utf-8 -*-

from app import app
import unittest

class FlaskrTestCase(unittest.TestCase):
    
    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()
    
    def tearDown(self):
        pass

    def test_index(self):
        rv = self.app.get('/')
        assert rv.status == '200 OK'

    def test_issues(self):
        rv = self.app.get('/themen')
        assert rv.status == '200 OK'

    def test_issue(self):
        rv = self.app.get('/themen/1')
        assert rv.status == '200 OK'

    def test_initiative(self):
        rv = self.app.get('/initiative/1')
        assert rv.status == '200 OK'

    def test_policies(self):
        rv = self.app.get('/regelwerke')
        assert rv.status == '200 OK'

    def test_policy(self):
        rv = self.app.get('/regelwerke/1')
        assert rv.status == '200 OK'

    def test_units(self):
        rv = self.app.get('/gliederungen')
        assert rv.status == '200 OK'

    def test_unit(self):
        rv = self.app.get('/gliederungen/1')
        assert rv.status == '200 OK'

    def test_areas(self):
        rv = self.app.get('/themenbereiche')
        assert rv.status == '200 OK'

    def test_area(self):
        rv = self.app.get('/themenbereiche/1')
        assert rv.status == '200 OK'

    def test_events(self):
        rv = self.app.get('/ereignisse')
        assert rv.status == '200 OK'

    def test_members(self):
        rv = self.app.get('/mitglieder')
        assert '''    <ul class="unstyled">
      
    </ul>''' in rv.data
        assert rv.status == '200 OK'

    def test_member(self):
        rv = self.app.get('/mitglieder/1')
        assert rv.status == '403 FORBIDDEN'

    def test_settings(self):
        rv = self.app.get('/einstellungen')
        assert rv.status == '200 OK'

        rv = self.app.post('/einstellungen', data={'submit_key': '', 'api_key': 'abc'})
        assert rv.status == '200 OK'
        assert 'Dein API-Schlüssel wurde nicht akzeptiert.' in rv.data

        rv = self.app.post('/einstellungen', data={'delete_key': ''})
        assert rv.status == '200 OK'
        assert 'Der API-Schlüssel wurde gelöscht.' in rv.data

if __name__ == '__main__':
    unittest.main()
