# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding M2M table for field tags on 'Source'
        db.create_table('recipes_source_tags', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('source', models.ForeignKey(orm['recipes.source'], null=False)),
            ('tag', models.ForeignKey(orm['recipes.tag'], null=False))
        ))
        db.create_unique('recipes_source_tags', ['source_id', 'tag_id'])


    def backwards(self, orm):
        
        # Removing M2M table for field tags on 'Source'
        db.delete_table('recipes_source_tags')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'recipes.downloadtask': {
            'Meta': {'object_name': 'DownloadTask'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'download_url': ('django.db.models.fields.URLField', [], {'unique': 'True', 'max_length': '255'}),
            'forum_url': ('django.db.models.fields.URLField', [], {'max_length': '255', 'blank': 'True'}),
            'home_url': ('django.db.models.fields.URLField', [], {'max_length': '255', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['recipes.Level']"}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'problem': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'blank': 'True'}),
            'recipe': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['recipes.Spec']"}),
            'remix': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['recipes.Remix']", 'null': 'True', 'blank': 'True'})
        },
        'recipes.level': {
            'Meta': {'ordering': "['-released']", 'object_name': 'Level'},
            'desc': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'released': ('django.db.models.fields.DateTimeField', [], {})
        },
        'recipes.packarg': {
            'Meta': {'unique_together': "[('recipe_pack', 'name')]", 'object_name': 'PackArg'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'}),
            'recipe_pack': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'pack_args'", 'to': "orm['recipes.Remix']"}),
            'source_pack': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'occurrences'", 'to': "orm['recipes.Release']"})
        },
        'recipes.release': {
            'Meta': {'ordering': "['-released']", 'object_name': 'Release'},
            'download_url': ('django.db.models.fields.URLField', [], {'unique': 'True', 'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'last_download_attempt': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(1970, 1, 1, 1, 0)'}),
            'level': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'source_packs'", 'to': "orm['recipes.Level']"}),
            'maps': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['recipes.Spec']", 'null': 'True', 'blank': 'True'}),
            'released': ('django.db.models.fields.DateTimeField', [], {}),
            'series': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'releases'", 'to': "orm['recipes.Source']"})
        },
        'recipes.remix': {
            'Meta': {'object_name': 'Remix'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'recipe': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'occurrences'", 'to': "orm['recipes.Spec']"}),
            'withdrawn': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'withdrawn_reason': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200', 'blank': 'True'})
        },
        'recipes.source': {
            'Meta': {'object_name': 'Source'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'forum_url': ('django.db.models.fields.URLField', [], {'max_length': '255', 'blank': 'True'}),
            'home_url': ('django.db.models.fields.URLField', [], {'max_length': '255', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['recipes.Tag']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'recipes.spec': {
            'Meta': {'ordering': "['spec_type', 'label']", 'unique_together': "[('name', 'spec_type')]", 'object_name': 'Spec'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'desc': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.SlugField', [], {'max_length': '200', 'db_index': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'spec': ('django.db.models.fields.TextField', [], {}),
            'spec_type': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['recipes.Tag']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'recipes.tag': {
            'Meta': {'object_name': 'Tag'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'name': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '200', 'db_index': 'True'})
        }
    }

    complete_apps = ['recipes']
