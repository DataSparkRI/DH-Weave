from weave.models import *

def get_or_create_data_table(tbl_name):
    """ get or create a new data table into Weave Meta info
        Returns an entity_id
    """
    sync_db_sequence()
    REQUIRED_PRIVATE_META = (
        ('importMethod', 'Portal Indicator'),
        ('sqlSchema', 'public'),
        ('sqlTable', 'indicator_indicatordata'),
    )

    REQUIRED_PUBLIC_META = (
        ('title', tbl_name),
    )

    try:
        # try to find a meta entry with this name, it may be what we are
        # looking for
        m = WeaveMetaPublic.objects.get(meta_name='title',meta_value=tbl_name)
        return m.entity_id

    except WeaveMetaPublic.DoesNotExist:

        w_manifest = WeaveManifest(type_id=0) # data tables are always type_id=0
        w_manifest.save()

        # now we need to create required public/private sets of meta data for this Data
        # Table
        for pm in REQUIRED_PRIVATE_META:
            WeaveMetaPrivate(entity_id=w_manifest.entity_id, meta_name=pm[0], meta_value=pm[1]).save()

        for pm in REQUIRED_PUBLIC_META:
            WeaveMetaPublic(entity_id=w_manifest.entity_id, meta_name=pm[0], meta_value=pm[1]).save()

        return w_manifest.pk


def insert_data_row(parent_id, title, data_type, sql_query):
    """ Insert a data entity and create relationship to parent entity"""
    sync_db_sequence()

    REQUIRED_PRIVATE_META = (
        ('sqlQuery', sql_query),
        ('sqlSchema', 'public'),
        ('sqlTable', 'indicator_indicatordata'),
    )

    REQUIRED_PUBLIC_META = (
        ('title', title),
        ('dataType', data_type),

    )
    # create an entry in weave_manifest
    m = WeaveManifest(type_id=1)
    m.save()

    # create a relationship in hierarachy table
    count = WeaveHierarchy.objects.filter(parent_id=parent_id).count()
    WeaveHierarchy(parent_id=parent_id, child_id=m.pk, sort_order=count+1).save()

    for pm in REQUIRED_PRIVATE_META:
        WeaveMetaPrivate(entity_id=m.entity_id, meta_name=pm[0], meta_value=pm[1]).save()

    for pm in REQUIRED_PUBLIC_META:
        WeaveMetaPublic(entity_id=m.entity_id, meta_name=pm[0], meta_value=pm[1]).save()



# We are using a combination of Django and Weave to insert records into the
# weave Tables. Because we are doing that, we need to make sure to resuet the
# squence from which auoomaticvalues are generated. We can use the management
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
