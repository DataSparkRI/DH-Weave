from django.db import models
from django.contrib.auth.models import User
from weave.managers import *
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
import cgi
from django.conf import settings

class Image(models.Model):
    photo = models.ImageField(upload_to='image')

    def save(self, *args, **kwargs):
        from shutil import copy2
        super(Image, self).save(*args, **kwargs)
        copy2(self.photo.path, settings.WEAVE_STORAGE)

    def __unicode__(self):
        return self.photo.name


class HubEntityIndex(models.Model):
    """ A foreign key index for all Hub Created Weave Meta Fields """
    created_at = models.DateTimeField(auto_now_add=True)

class WeaveManifest(models.Model):
    h_e_index = models.ForeignKey(HubEntityIndex, null=True)
    entity_id = models.AutoField(primary_key=True, db_index=True)
    type_id = models.SmallIntegerField()

    class Meta:
        db_table = "weave_manifest"

    def __unicode__(self):
        return "Entity Id: %s" % self.entity_id


class WeaveMeta(models.Model):
    """ Abstract class for weave_meta_private and weave_meta_public"""
    h_e_index = models.ForeignKey(HubEntityIndex, null=True)
    entity_id = models.BigIntegerField(db_index=True) # this is not a ForiegnKey on purpose
    meta_name = models.CharField(max_length=255, db_index=True)
    meta_value = models.CharField(max_length=2048, blank=True, db_index=True)

    class Meta:
        abstract = True

    def __unicode__(self):
        return "E_id: %s Name: %s Value: %s" % (self.entity_id, self.meta_name, self.meta_value)

class WeaveFlatPublicMeta(models.Model):
    """ A flat aggregate version of weave public meta"""
    h_e_index = models.ForeignKey(HubEntityIndex, null=True)
    weaveEntityId = models.BigIntegerField(db_index=True)
    min = models.CharField(max_length=255, blank=True, null=True)
    max = models.CharField(max_length=255, blank=True, null=True)
    dataType = models.CharField(max_length=255, blank=True, null=True)
    keyType = models.CharField(max_length=255, blank=True, null=True)
    object_id = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    year = models.CharField(max_length=255, blank=True, null=True)
    dataTable = models.CharField(max_length=255, blank=True, null=True)


    def to_dict(self):
        d = {
                'weaveEntityId':  self.weaveEntityId,
                'min' : self.min,
                'max' : self.max,
                'dataType': self.dataType,
                'keyType': self.keyType,
                'object_id': self.object_id,
                'title': self.title,
                'name': self.name,
                'year': self.year,
                'dataTable':self.dataTable,
        }
        return d

    def to_ds_dict(self):
        d = {
                '-weaveEntityId':  self.weaveEntityId,
                '-min' : self.min,
                '-max' : self.max,
                '-dataType': self.dataType,
                '-keyType': self.keyType,
                '-object_id': self.object_id,
                '-title': self.title,
                '-name': self.name,
                '-year': self.year,
                '-dataTable':self.dataTable,
        }
        return d

    def to_xml_attr(self):
        return u'''<attribute title="{title}" year="{year}" object_id="{id}" dataType="{datatype}" dataTable="{datatable}" keyType="{keytype}" weaveEntityId="{entityid}" name="{name}"/>'''.format(title=cgi.escape(self.title), year=self.year, id=self.object_id, datatype=self.dataType, datatable=self.dataTable, keytype=self.keyType, entityid=self.weaveEntityId, name=cgi.escape(self.name))

    def __unicode__(self):
        if self.title:
            return self.title
        else:
            return "Related to %s" % self.h_e_index


class WeaveMetaPublic(WeaveMeta):
    class Meta:
        db_table="weave_meta_public"

class WeaveMetaPrivate(WeaveMeta):
    class Meta:
        db_table="weave_meta_private"


class WeaveHierarchy(models.Model):
    h_e_index = models.ForeignKey(HubEntityIndex, null=True)
    parent_id = models.BigIntegerField(db_index=True)
    child_id = models.BigIntegerField(db_index=True)
    sort_order = models.IntegerField()

    class Meta:
        db_table = "weave_hierarchy"

    def __unicode__(self):
        return "parent_id:{0} child_id:{1}".format(self.parent_id, self.child_id)


class DataFilter(models.Model):
    file = models.FileField(upload_to='data_filter_files', blank=True)
    name = models.CharField(max_length=100, unique=True)
    display = models.BooleanField(default=True)
    key_unit_type = models.CharField(max_length=256)

    def save(self, *args, **kwargs):
        super(DataFilter, self).save(*args, **kwargs)

        # clear out exiting data keys
        DataFilterKey.objects.filter(data_filter=self).delete()
        # read the file and generate DataFilterKeys
        self.file.open()
        for l in self.file.readlines():
            # strip out leading and trailing white spaces
            l = l.strip()
            # only save non empty strings
            if l != "":
                self.datafilterkey_set.create(key_value=l)

        self.file.close()

    def __unicode__(self):
        return self.name


class DataFilterKey(models.Model):
    data_filter = models.ForeignKey(DataFilter)
    key_value = models.CharField(max_length=100)

    def __unicode__(self):
        return u"%s - %s" % (self.data_filter, self.key_value)


class ClientConfiguration(models.Model):
    FORMAT_CHOICES = (
        ('json', 'json'),
        ('xml', 'xml'),
        ('file', 'file')
    )
    content_type = models.ForeignKey(ContentType, null=True, help_text='If you are creating a Data Story Page, this should be "page".')
    object_id = models.PositiveIntegerField(null=True, blank=True) # this has nothing to do with Weave's object_id
    content_object = generic.GenericForeignKey('content_type', 'object_id') # Generic relationship to lots of different models.
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, db_index=True, blank=True)
    content = models.TextField(default='', blank=True)
    # name of the file, relative to Tomcat's/weave's docroot. This will be passed on as
    # as a url to the weave client
    content_file = models.CharField(max_length=100, unique=True, null=True, blank=True)
    content_format = models.CharField(max_length=4, choices=FORMAT_CHOICES, default='file', null=True)
    image = models.ImageField(upload_to='weave_images', blank=True, null=True)
    is_public = models.NullBooleanField(default=False, null=True, blank=True)

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
        return "%s" % self.content_file

    def __unicode__(self):
        return "%s" % self.name
    class Meta:
        ordering = ('name',)


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

