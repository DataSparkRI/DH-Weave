# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'WeaveManifest'
        db.create_table('weave_manifest', (
            ('entity_id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('type_id', self.gf('django.db.models.fields.SmallIntegerField')()),
        ))
        db.send_create_signal(u'weave', ['WeaveManifest'])

        # Adding model 'WeaveMetaPublic'
        db.create_table('weave_meta_public', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('entity_id', self.gf('django.db.models.fields.BigIntegerField')()),
            ('meta_name', self.gf('django.db.models.fields.CharField')(max_length=255, db_index=True)),
            ('meta_value', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=2048, blank=True)),
        ))
        db.send_create_signal(u'weave', ['WeaveMetaPublic'])

        # Adding model 'WeaveMetaPrivate'
        db.create_table('weave_meta_private', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('entity_id', self.gf('django.db.models.fields.BigIntegerField')()),
            ('meta_name', self.gf('django.db.models.fields.CharField')(max_length=255, db_index=True)),
            ('meta_value', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=2048, blank=True)),
        ))
        db.send_create_signal(u'weave', ['WeaveMetaPrivate'])

        # Adding model 'WeaveHierarchy'
        db.create_table('weave_hierarchy', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('parent_id', self.gf('django.db.models.fields.BigIntegerField')()),
            ('child_id', self.gf('django.db.models.fields.BigIntegerField')()),
            ('sort_order', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'weave', ['WeaveHierarchy'])

        # Adding model 'ClientConfiguration'
        db.create_table(u'weave_clientconfiguration', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=50, blank=True)),
            ('content', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('content_file', self.gf('django.db.models.fields.CharField')(max_length=100, unique=True, null=True, blank=True)),
            ('content_format', self.gf('django.db.models.fields.CharField')(default='file', max_length=4)),
            ('is_public', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'weave', ['ClientConfiguration'])


    def backwards(self, orm):
        # Deleting model 'WeaveManifest'
        db.delete_table('weave_manifest')

        # Deleting model 'WeaveMetaPublic'
        db.delete_table('weave_meta_public')

        # Deleting model 'WeaveMetaPrivate'
        db.delete_table('weave_meta_private')

        # Deleting model 'WeaveHierarchy'
        db.delete_table('weave_hierarchy')

        # Deleting model 'ClientConfiguration'
        db.delete_table(u'weave_clientconfiguration')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'weave.clientconfiguration': {
            'Meta': {'object_name': 'ClientConfiguration'},
            'content': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'content_file': ('django.db.models.fields.CharField', [], {'max_length': '100', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'content_format': ('django.db.models.fields.CharField', [], {'default': "'file'", 'max_length': '4'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'weave.weavehierarchy': {
            'Meta': {'object_name': 'WeaveHierarchy', 'db_table': "'weave_hierarchy'"},
            'child_id': ('django.db.models.fields.BigIntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parent_id': ('django.db.models.fields.BigIntegerField', [], {}),
            'sort_order': ('django.db.models.fields.IntegerField', [], {})
        },
        u'weave.weavemanifest': {
            'Meta': {'object_name': 'WeaveManifest', 'db_table': "'weave_manifest'"},
            'entity_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'type_id': ('django.db.models.fields.SmallIntegerField', [], {})
        },
        u'weave.weavemetaprivate': {
            'Meta': {'object_name': 'WeaveMetaPrivate', 'db_table': "'weave_meta_private'"},
            'entity_id': ('django.db.models.fields.BigIntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'meta_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'meta_value': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '2048', 'blank': 'True'})
        },
        u'weave.weavemetapublic': {
            'Meta': {'object_name': 'WeaveMetaPublic', 'db_table': "'weave_meta_public'"},
            'entity_id': ('django.db.models.fields.BigIntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'meta_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'meta_value': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '2048', 'blank': 'True'})
        }
    }

    complete_apps = ['weave']