from django.db import models


class WeaveManifest(models.Model):
    entity_id = models.AutoField(primary_key=True)
    type_id = models.SmallIntegerField()

    class Meta:
        db_table = "weave_manifest"

    def __unicode__(self):
        return "Entity Id: %s" % self.entity_id


class WeaveMeta(models.Model):
    """ Abstract class for weave_meta_private and weave_meta_public"""
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
    parent_id = models.BigIntegerField()
    child_id = models.BigIntegerField()
    sort_order = models.IntegerField()

    class Meta:
        db_table = "weave_hierarchy"

    def __unicode__(self):
        return "parent_id:{0} child_id:{1}".format(self.parent_id, self.child_id)







