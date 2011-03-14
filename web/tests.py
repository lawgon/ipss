from django.test import TestCase
from web.models import City
from django.test.client import Client



class SourceTestCase(TestCase):
    fixtures = ['source.json']
    def setUp(self):
        self.client = Client()

        
    def testSource(self):
        response = self.client.get('/addcity/')
        self.assertEqual(response.status_code, 302)

