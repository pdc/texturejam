# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding unique constraint on 'Spec', fields ['name', 'spec_type']
        db.create_unique('recipes_spec', ['name', 'spec_type'])

        # Adding unique constraint on 'PackArg', fields ['recipe_pack', 'name']
        db.create_unique('recipes_packarg', ['recipe_pack_id', 'name'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'PackArg', fields ['recipe_pack', 'name']
        db.delete_unique('recipes_packarg', ['recipe_pack_id', 'name'])

        # Removing unique constraint on 'Spec', fields ['name', 'spec_type']
        db.delete_unique('recipes_spec', ['name', 'spec_type'])


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
            'recipe_pack': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'pack_args'", 'to': "orm['recipes.RecipePack']"}),
            'source_pack': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'occurrences'", 'to': "orm['recipes.SourcePack']"})
        },
        'recipes.recipepack': {
            'Meta': {'object_name': 'RecipePack'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'recipe_packs'", 'to': "orm['auth.User']"}),
            'recipe': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'occurrences'", 'to': "orm['recipes.Spec']"}),
            'withdrawn': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'withdrawn_reason': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200', 'blank': 'True'})
        },
        'recipes.sourcepack': {
            'Meta': {'ordering': "['-released']", 'object_name': 'SourcePack'},
            'download_url': ('django.db.models.fields.URLField', [], {'unique': 'True', 'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'last_download_attempt': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(1970, 1, 1, 1, 0)'}),
            'level': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'source_packs'", 'to': "orm['recipes.Level']"}),
            'released': ('django.db.models.fields.DateTimeField', [], {}),
            'series': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'releases'", 'to': "orm['recipes.SourceSeries']"})
        },
        'recipes.sourceseries': {
            'Meta': {'object_name': 'SourceSeries'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'forum_url': ('django.db.models.fields.URLField', [], {'max_length': '255', 'blank': 'True'}),
            'home_url': ('django.db.models.fields.URLField', [], {'max_length': '255', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'source_series'", 'to': "orm['auth.User']"})
        },
        'recipes.spec': {
            'Meta': {'ordering': "['spec_type', 'label']", 'unique_together': "[('name', 'spec_type')]", 'object_name': 'Spec'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'desc': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.SlugField', [], {'max_length': '200', 'db_index': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'atlases'", 'to': "orm['auth.User']"}),
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
