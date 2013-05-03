from django.db import models
from django.contrib.auth.models import User
from weave.managers import *
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic


class HubEntityIndex(models.Model):
    """ A foreign key index for all Hub Created Weave Meta Fields """
    created_at = models.DateTimeField(auto_now_add=True)

class WeaveManifest(models.Model):
    h_e_index = models.ForeignKey(HubEntityIndex, null=True)
    entity_id = models.AutoField(primary_key=True)
    type_id = models.SmallIntegerField()

    class Meta:
        db_table = "weave_manifest"

    def __unicode__(self):
        return "Entity Id: %s" % self.entity_id


class WeaveMeta(models.Model):
    """ Abstract class for weave_meta_private and weave_meta_public"""
    h_e_index = models.ForeignKey(HubEntityIndex, null=True)
    entity_id = models.BigIntegerField() # this is not a ForiegnKey on purpose
    meta_name = models.CharField(max_length=255, db_index=True)
    meta_value = models.CharField(max_length=2048, blank=True, db_index=True)

    class Meta:
        abstract = True

    def __unicode__(self):
        return "E_id: %s Name: %s Value: %s" % (self.entity_id, self.meta_name, self.meta_value)


class WeaveMetaPublic(WeaveMeta):
    class Meta:
        db_table="weave_meta_public"

class WeaveMetaPrivate(WeaveMeta):
    class Meta:
        db_table="weave_meta_private"


class WeaveHierarchy(models.Model):
    h_e_index = models.ForeignKey(HubEntityIndex, null=True)
    parent_id = models.BigIntegerField()
    child_id = models.BigIntegerField()
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
    content_object = generic.GenericForeignKey('content_type', 'object_id') # Generic relationship to lots of different models.
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, db_index=True, blank=True)
    content = models.TextField(default='', blank=True)
    # name of the file, relative to Tomcat's/weave's docroot. This will be passed on as
    # as a url to the weave client
    content_file = models.CharField(max_length=100, unique=True, null=True, blank=True)
    content_format = models.CharField(max_length=4, choices=FORMAT_CHOICES, default='file')
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

