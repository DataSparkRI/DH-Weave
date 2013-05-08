# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'ClientConfiguration.content_format'
        db.alter_column('weave_clientconfiguration', 'content_format', self.gf('django.db.models.fields.CharField')(max_length=4, null=True))

    def backwards(self, orm):

        # Changing field 'ClientConfiguration.content_format'
        db.alter_column('weave_clientconfiguration', 'content_format', self.gf('django.db.models.fields.CharField')(max_length=4))

    models = {
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'weave.clientconfiguration': {
            'Meta': {'object_name': 'ClientConfiguration'},
            'content': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'content_file': ('django.db.models.fields.CharField', [], {'max_length': '100', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'content_format': ('django.db.models.fields.CharField', [], {'default': "'file'", 'max_length': '4', 'null': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']", 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_public': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50', 'blank': 'True'})
        },
        'weave.datafilter': {
            'Meta': {'object_name': 'DataFilter'},
            'display': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key_unit_type': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
        },
        'weave.datafilterkey': {
            'Meta': {'object_name': 'DataFilterKey'},
            'data_filter': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['weave.DataFilter']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key_value': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'weave.hubentityindex': {
            'Meta': {'object_name': 'HubEntityIndex'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'weave.weavehierarchy': {
            'Meta': {'object_name': 'WeaveHierarchy', 'db_table': "'weave_hierarchy'"},
            'child_id': ('django.db.models.fields.BigIntegerField', [], {}),
            'h_e_index': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['weave.HubEntityIndex']", 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parent_id': ('django.db.models.fields.BigIntegerField', [], {}),
            'sort_order': ('django.db.models.fields.IntegerField', [], {})
        },
        'weave.weavemanifest': {
            'Meta': {'object_name': 'WeaveManifest', 'db_table': "'weave_manifest'"},
            'entity_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'h_e_index': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['weave.HubEntityIndex']", 'null': 'True'}),
            'type_id': ('django.db.models.fields.SmallIntegerField', [], {})
        },
        'weave.weavemetaprivate': {
            'Meta': {'object_name': 'WeaveMetaPrivate', 'db_table': "'weave_meta_private'"},
            'entity_id': ('django.db.models.fields.BigIntegerField', [], {}),
            'h_e_index': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['weave.HubEntityIndex']", 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'meta_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'meta_value': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '2048', 'blank': 'True'})
        },
        'weave.weavemetapublic': {
            'Meta': {'object_name': 'WeaveMetaPublic', 'db_table': "'weave_meta_public'"},
            'entity_id': ('django.db.models.fields.BigIntegerField', [], {}),
            'h_e_index': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['weave.HubEntityIndex']", 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'meta_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'meta_value': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '2048', 'blank': 'True'})
        }
    }

    complete_apps = ['weave']