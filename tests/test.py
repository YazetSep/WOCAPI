import unittest
from flask.ext.testing import TestCase 
from ../__init__ import app, db
from ../models import Users, Events
import flask_testing

class BaseTestCase(TestCase): 
    """A Base test case.""" 
    def create_app(self): 
        app.config.from_object('config.TestConfig') 
        return app 

    def setUp(self): 
        db.create_all() 
        #db.session.add(Event("Test event", "this is a test event.")) 
        #db.session.add(User("admin", "ad@min.com", "admin")) 
        #db.session.commit() 

    def tearDown(self): 
        db.session.remove() 
        db.drop_all() 

class FlaskTestCase(BaseTestCase): 
    def test_index(self): 
        response = self.client.get('/login', content_type='html/text') 
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
