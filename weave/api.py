from weave.models import *
from django.conf import settings

WEAVE_SETTINGS = getattr(settings, "WEAVE", {})
WEAVE_CONNECTION = getattr(WEAVE_SETTINGS, 'CONNECTION', "local")

def get_or_create_data_table(tbl_name):
    """ get or create a new data table into Weave Meta info
        Returns an entity_id
        This should create
            1 HubEntityIndex
            1 WeaveManifest
            4 WeaveMetaPrivate
            1 WeaveMetaPublic

    """
    sync_db_sequence()
    REQUIRED_PRIVATE_META = (
        ('importMethod', 'Portal Indicator'),
        ('sqlSchema', 'public'),
        ('sqlTable', 'indicator_indicatordata'),
        ('connection', WEAVE_CONNECTION ),
    )

    REQUIRED_PUBLIC_META = (
        ('title', tbl_name),
    )

    hei = HubEntityIndex()
    hei.save()

    try:
        # try to find a meta entry with this name, it may be what we are
        # looking for
        m = WeaveMetaPublic.objects.get(meta_name='title',meta_value=tbl_name)
        return m.entity_id

    except WeaveMetaPublic.DoesNotExist:

        w_manifest = WeaveManifest(h_e_index=hei, type_id=0) # data tables are always type_id=0
        w_manifest.save()

        # now we need to create required public/private sets of meta data for this Data
        # Table
        for pm in REQUIRED_PRIVATE_META:
            WeaveMetaPrivate(h_e_index=hei, entity_id=w_manifest.entity_id, meta_name=pm[0], meta_value=pm[1]).save()

        for pm in REQUIRED_PUBLIC_META:
            WeaveMetaPublic(h_e_index=hei, entity_id=w_manifest.entity_id, meta_name=pm[0], meta_value=pm[1]).save()

        return w_manifest.pk


def insert_data_row(parent_id, title, data_type, sql_query):
    """ Insert a data entity and create relationship to parent entity
        This should create
            1 HubEntityIndex
            1 Weave Manifest
            1 WeaveHeirchy
            5 WeaveMetaPrivate
            2 WeaveMetaPublic
    """
    sync_db_sequence()

    REQUIRED_PRIVATE_META = (
        ('sqlQuery', sql_query),
        ('sqlSchema', 'public'),
        ('sqlTable', 'indicator_indicatordata'),
        ('importMethod', 'Portal Indicator'),
        ('connection', WEAVE_CONNECTION ),

    )

    REQUIRED_PUBLIC_META = (
        ('title', title),
        ('dataType', data_type),

    )

    hei = HubEntityIndex()
    hei.save()

    # create an entry in weave_manifest
    m = WeaveManifest(h_e_index=hei, type_id=1)
    m.save()

    # create a relationship in hierarachy table
    count = WeaveHierarchy.objects.filter(parent_id=parent_id).count()
    WeaveHierarchy(h_e_index=hei, parent_id=parent_id, child_id=m.pk, sort_order=count+1).save()

    for pm in REQUIRED_PRIVATE_META:
        WeaveMetaPrivate(h_e_index=hei, entity_id=m.entity_id, meta_name=pm[0], meta_value=pm[1]).save()

    for pm in REQUIRED_PUBLIC_META:
        WeaveMetaPublic(h_e_index=hei, entity_id=m.entity_id, meta_name=pm[0], meta_value=pm[1]).save()


def clear_generated_meta():
    """ Clear out all the weave meta generated by the the weave django app"""
    hubs = HubEntityIndex.objects.all()
    for h in hubs:
        rels = [rel.get_accessor_name() for rel in h._meta.get_all_related_objects()]
        for r in rels:
            objects = getattr(h, r).all().delete()
        h.delete()

def get_hierarchy_as_xml():
    """ Return weave data heirchy as xml categories """
    out = ""
    parent_ids = WeaveHierarchy.objects.all().distinct('parent_id')

    for p in parent_ids:
        p_meta = WeaveMetaPublic.objects.get(entity_id=p.parent_id, meta_name="title")
        xml = WeaveXMLSet(p_meta.meta_value, p.parent_id)

        # now add attibute nodes
        # get all the Heirarchy objects that belong to this parent id
        for h_obj in WeaveHierarchy.objects.filter(parent_id=p.parent_id):
            title = WeaveMetaPublic.objects.get(entity_id=h_obj.child_id, meta_name="title").meta_value
            datatype = WeaveMetaPublic.objects.get(entity_id=h_obj.child_id, meta_name="dataType").meta_value
            xml.add_attribute(title, datatype, h_obj.child_id)


        out += xml.render()

    return out

def get_custom_hierarchy_as_xml(title, hierarchy_list_items):
    """ Generate a custom hierarchy bases on the the h_list_items
        the h_list_items should be a list of dicts that follow this ex:
        [{
            'title':'My thing',
            'datatype':'string or number',
            'weave_entity_id':<a proper weave entity>,
        }]
    """
    xml = WeaveXMLSet(title=title, weave_entity_id="99999")
    for item in hierarchy_list_items:
        xml.add_attribute(**item)

    return xml.render()



class WeaveXMLSet():
    def __init__(self, title, weave_entity_id):
        self.title = title
        self.weave_entity_id = weave_entity_id
        self.attributes = []

    def add_attribute(self, title, datatype, weave_entity_id=None):
        self.attributes.append({
            'title':title,
            'datatype':datatype,
            'weave_entity_id':weave_entity_id if weave_entity_id is not None else self.get_weave_entity_id(title),
        })

    def get_weave_entity_id(self, title):
        """ Look up a for realz weave entity id by title"""
        print title
        return WeaveMetaPublic.objects.get(meta_name='title', meta_value=title).entity_id

    def render(self):
        cat_head = """<category title="{0}" weaveEntityId="{1}" >""".format(self.title, self.weave_entity_id)
        cat_foot = """</category>"""
        attrs_nodes = ""
        for atr in self.attributes:
            node = """<attribute title="{title}" dataType="{datatype}" weaveEntityId="{weave_entity_id}"/>""".format(**atr)
            attrs_nodes += node + "\n"

        return "%s\n%s%s\n" % (cat_head, attrs_nodes, cat_foot)



# We are using a combination of Django and Weave to insert records into the
# weave Tables. Because we are doing that, we need to make sure to reset the
# squence from which automaticvalues are generated. We can use the management
# 'sqlsequencereset' to get the sql to do that, then pass that into a db cursor
# and execute it.

class Alf(object):
    pass


def sync_db_sequence():
    from django.core.management import call_command
    from django.db import connection
    import sys, StringIO, contextlib

    @contextlib.contextmanager
    def capture_stdout():
        old = sys.stdout
        capturer = StringIO.StringIO()
        sys.stdout = capturer
        data = Alf()
        yield data
        sys.stdout = old
        data.result = capturer.getvalue()

    with capture_stdout() as capture:
        call_command('sqlsequencereset', 'weave')
    cursor = connection.cursor()
    cursor.execute(capture.result)


class ClientConfiguration(models.Model):
    FORMAT_CHOICES = (
        ('json', 'json'),
        ('xml', 'xml'),
        ('file', 'file')
    )
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, db_index=True)
    content = models.TextField(default='', blank=True)  # TODO: add minimal config
    # name of the file, relative to Tomcat's/weave's docroot. This will be passed on as
    # as a url to the weave client
    content_file = models.CharField(max_length=100, unique=True, null=True, blank=True)
    content_format = models.CharField(max_length=4, choices=FORMAT_CHOICES, default='file')

    def cc_type(self):
        is_user_generated = self.weavefile_set.all().count() > 0
        in_datastory = self.page_set.all().count() > 0
        in_report = self.report_set.all().count() > 0

        return 'ug: %s / ds: %s / rpt: %s' % (is_user_generated, in_datastory, in_report)

    cc_type.short_description = 'CC Type'

    def save(self, *args, **kwargs):
        from weave.util import unique_slugify
        unique_slugify(self, self.name)
        super(ClientConfiguration, self).save(*args, **kwargs)

    @property
    def location_for_client(self):
        """ The url or path that should be passed to the Weave client to load this config """

        if self.content_format not in ('file', ):
            raise NotImplemented('Only file-based configs may be saved at this time')

        return "/weave_docroot/%s" % self.content_file

    def __unicode__(self):
        return "%s" % self.name

class CCDataStory(ClientConfiguration):
    class Meta:
        proxy = True
        verbose_name_plural = 'Client configurations (Datastory)'
        verbose_name = 'Client configuration (Datastory)'

    def __unicode__(self):
        return "%s" % self.name

    objects = CCDataStoryManager()

class CCReport(ClientConfiguration):
    class Meta:
        proxy = True
        verbose_name_plural = 'Client configurations (Report)'
        verbose_name = 'Client configuration (Report)'

    def __unicode__(self):
        return "%s" % self.name

    objects = CCReportManager()

class CCUserGenerated(ClientConfiguration):
    class Meta:
        proxy = True
        verbose_name_plural = 'Client configurations (User-generated)'
        verbose_name = 'Client configuration (User-generated)'
    def __unicode__(self):
        return "%s" % self.name

    objects = CCUserGeneratedManager()


class CCUnassigned(ClientConfiguration):
    class Meta:
        proxy = True
        verbose_name_plural = 'Client configurations (Unassigned)'
        verbose_name = 'Client configuration (Unassigned)'

    def __unicode__(self):
        return "%s" % self.name

    objects = CCUnassignedManager()
