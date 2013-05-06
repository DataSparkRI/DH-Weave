from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User
import simplejson as json

from weave.models import *
from weave.api import *

class APITest(TestCase):

    def test_get_or_create_data_table(self):
        get_or_create_data_table("testtable")
        # now we can just count the expected tables
        self.assertEqual(HubEntityIndex.objects.all().count(), 1)
        hei = HubEntityIndex.objects.all()[0]
        self.assertEqual(hei.weavemanifest_set.all().count(), 1)
        self.assertEqual(hei.weavemetaprivate_set.all().count(), 4)
        self.assertEqual(hei.weavemetapublic_set.all().count(), 1)
        clear_generated_meta()


    def test_insert_data_row(self):
        insert_data_row(1, "test", "test", 1, sql_query="SELECT * FROM TEST", object_id='1', year="2012")
        # now we can just count the expected tables
        self.assertEqual(HubEntityIndex.objects.all().count(), 1)
        hei = HubEntityIndex.objects.all()[0]
        self.assertEqual(hei.weavemanifest_set.all().count(), 1)
        self.assertEqual(hei.weavemetaprivate_set.all().count(), 5)
        self.assertEqual(hei.weavehierarchy_set.all().count(), 1)
        self.assertEqual(hei.weavemetapublic_set.all().count(), 7)
        clear_generated_meta()

    def test_xml_hierachy(self):
        p1 = get_or_create_data_table("testtable1")
        p2 = get_or_create_data_table("testtable2")
        p3 = get_or_create_data_table("testtable3")
        insert_data_row(p1, "test", 'test', 1, sql_query="SELECT * FROM TEST", object_id="1", year="2012")
        insert_data_row(p2, "te33333st",'test3333st',  1, sql_query="SELECT * FROM TEST",object_id="2", year="2012")
        insert_data_row(p3, "te33st","teawte", 1, sql_query="SELECT * FROM TEST",object_id="3", year="2012")
        insert_data_row(p3, "tesdafdt","aewtawet", 1, sql_query="SELECT * FROM TEST", object_id="4", year="2012")
        insert_data_row(p3, "terae","awet", 1,  sql_query="SELECT * FROM TEST", object_id="5", year="2012")
        expected = '<category title="testtable1" weaveEntityId="1" >\n<attribute title="test" dataType="1" weaveEntityId="4" object_id="1"/>\n</category>\n<category title="testtable2" weaveEntityId="2" >\n<attribute title="te33333st" dataType="1" weaveEntityId="5" object_id="2"/>\n</category>\n<category title="testtable3" weaveEntityId="3" >\n<attribute title="te33st" dataType="1" weaveEntityId="6" object_id="3"/>\n<attribute title="tesdafdt" dataType="1" weaveEntityId="7" object_id="4"/>\n<attribute title="terae" dataType="1" weaveEntityId="8" object_id="5"/>\n</category>\n'
        self.assertEqual(get_hierarchy_as_xml(), expected)
        clear_generated_meta()

    def test_custom_xml_hierarchy(self):
        items = [{
            'title':'test1',
            'datatype':'string',
            'weave_entity_id':'5',
        }]
        expected='<category title="TestCat" weaveEntityId="99999" >\n<attribute title="test1" dataType="string" weaveEntityId="5" object_id="0000"/>\n</category>\n'

        self.assertEqual(get_custom_hierarchy_as_xml('TestCat', items), expected)

class ClientConfigTest(TestCase):
    urls = 'weave.urls'

    def setUp(self):
        self.test_user = User.objects.create_user('tuser', 'temporary@gmail.com', 'tuser')
        self.test_user2 = User.objects.create_user('tuser2', 'temporar2y@gmail.com', 'tuser2')

    def test_relationships(self):
        # create some fake configs
        json_conf = ClientConfiguration(content_object=self.test_user, name="jsonconf", slug="jsonconf", content_format="json", is_public=True)
        json_conf.content = json.dumps({'a':'Hello World'})
        json_conf.save()

        print json_conf.content_object, json_conf.name, json_conf.object_id


class ViewsTest(TestCase):
    urls = 'weave.urls'

    def setUp(self):
        self.test_user = User.objects.create_user('tuser', 'temporary@gmail.com', 'tuser')
        self.test_user2 = User.objects.create_user('tuser2', 'temporar2y@gmail.com', 'tuser2')
        # create some fake configs
        json_conf = ClientConfiguration(content_object=self.test_user, name="jsonconf", slug="jsonconf", content_format="json", is_public=True)
        json_conf.content = json.dumps({'a':'Hello World'})
        json_conf.save()

        xml_conf = ClientConfiguration(content_object=self.test_user2, name="xmlconf", slug="xmlconf", content_format="xml")
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
        #response = client.get('/cc/xmlconf')
        #self.assertEqual(response.status_code, 404) # this fails when you test it in the context of another app with 404 page

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












