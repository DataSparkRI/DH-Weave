from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User
import simplejson as json

from weave.models import *

class ViewsTest(TestCase):
    urls = 'weave.urls'

    def setUp(self):
       self.test_user = User.objects.create_user('tuser', 'temporary@gmail.com', 'tuser')
       self.test_user2 = User.objects.create_user('tuser2', 'temporar2y@gmail.com', 'tuser2')
       # create some fake configs
       json_conf = ClientConfiguration(user=self.test_user, name="jsonconf", slug="jsonconf", content_format="json", is_public=True)
       json_conf.content = json.dumps({'a':'Hello World'})
       json_conf.save()

       xml_conf = ClientConfiguration(user=self.test_user2, name="xmlconf", slug="xmlconf", content_format="xml")
       xml_conf.content ='''
        <Weave>
            <thing></thing>
        </Weave>
       '''
       xml_conf.save()

    def test_cc_get_client_config(self):
        client = Client()
        # login the test user
        user = client.login(username='tuser', password='tuser')
        # get a conf that is not public or doesnt belong to this user
        response = client.get('/cc/xmlconf')
        self.assertEqual(response.status_code, 404)

        response = client.get('/cc/jsonconf')
        self.assertEqual(response.status_code, 200)

        # now try to get a public config with a generic client
        client = Client()
        response = client.get('/cc/jsonconf')
        self.assertEqual(response.status_code, 200)

    def test_cc_not_exists(self):
        client = Client()
        # login the test user
        user = client.login(username='tuser', password='tuser')
        response = client.post('/cc-save/newjson', {
                'cc_name':'UPDATED',
                'cc_data':json.dumps({'foob':'barf'})
        })
        self.assertEqual(3, ClientConfiguration.objects.all().count())

    def test_cc_save_exists(self):
        client = Client()

        #unauthenticated
        response = client.post('/cc-save/jsonconf', {
                'cc_name':'UPDATED',
                'cc_data':json.dumps({'foob':'barf'})
        })

        self.assertEqual(response.status_code, 302) # redirect to login

        # login the test user
        user = client.login(username='tuser', password='tuser')
        # get the origin content
        old = ClientConfiguration.objects.get(slug='jsonconf').content
        response = client.post('/cc-save/jsonconf', {
                'cc_name':'UPDATED',
                'cc_data':json.dumps({'foob':'barf'})
        })

        self.assertEqual(response.content, '{"status": "success-json", "cc-slug": "jsonconf"}')
        updated = ClientConfiguration.objects.get(slug='jsonconf').content

        self.assertNotEqual(updated, old)

    def test_cc_propertype(self):
        client = Client()
        # login the test user
        user = client.login(username='tuser', password='tuser')
        response = client.post('/cc-save/typejson', {
                'cc_name':'New Json',
                'cc_data':json.dumps({'foob':'barf'})
        })
        response = client.post('/cc-save/typexml', {
                'cc_name':'new xml',
                'cc_data':'<weave></weave>'
        })

        self.assertEqual('xml', ClientConfiguration.objects.get(slug='new-xml').content_format)
        self.assertEqual('json', ClientConfiguration.objects.get(slug='new-json').content_format)













