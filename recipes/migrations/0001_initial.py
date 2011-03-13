# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Level'
        db.create_table('recipes_level', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('desc', self.gf('django.db.models.fields.TextField')()),
            ('released', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal('recipes', ['Level'])

        # Adding model 'SourceSeries'
        db.create_table('recipes_sourceseries', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(related_name='source_series', to=orm['auth.User'])),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('home_url', self.gf('django.db.models.fields.URLField')(max_length=255, blank=True)),
            ('forum_url', self.gf('django.db.models.fields.URLField')(max_length=255, blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('recipes', ['SourceSeries'])

        # Adding model 'SourcePack'
        db.create_table('recipes_sourcepack', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('series', self.gf('django.db.models.fields.related.ForeignKey')(related_name='releases', to=orm['recipes.SourceSeries'])),
            ('level', self.gf('django.db.models.fields.related.ForeignKey')(related_name='source_packs', to=orm['recipes.Level'])),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('download_url', self.gf('django.db.models.fields.URLField')(unique=True, max_length=255)),
            ('released', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal('recipes', ['SourcePack'])

        # Adding model 'Spec'
        db.create_table('recipes_spec', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(related_name='atlases', to=orm['auth.User'])),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('name', self.gf('django.db.models.fields.SlugField')(max_length=200, db_index=True)),
            ('spec_type', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('spec', self.gf('django.db.models.fields.TextField')()),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('recipes', ['Spec'])

        # Adding model 'RecipePack'
        db.create_table('recipes_recipepack', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(related_name='recipe_packs', to=orm['auth.User'])),
            ('recipe', self.gf('django.db.models.fields.related.ForeignKey')(related_name='occurrences', to=orm['recipes.Spec'])),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=1000)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('recipes', ['RecipePack'])

        # Adding model 'PackArg'
        db.create_table('recipes_packarg', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('recipe_pack', self.gf('django.db.models.fields.related.ForeignKey')(related_name='pack_args', to=orm['recipes.RecipePack'])),
            ('source_pack', self.gf('django.db.models.fields.related.ForeignKey')(related_name='occurrences', to=orm['recipes.SourcePack'])),
            ('name', self.gf('django.db.models.fields.SlugField')(max_length=50, db_index=True)),
        ))
        db.send_create_signal('recipes', ['PackArg'])


    def backwards(self, orm):
        
        # Deleting model 'Level'
        db.delete_table('recipes_level')

        # Deleting model 'SourceSeries'
        db.delete_table('recipes_sourceseries')

        # Deleting model 'SourcePack'
        db.delete_table('recipes_sourcepack')

        # Deleting model 'Spec'
        db.delete_table('recipes_spec')

        # Deleting model 'RecipePack'
        db.delete_table('recipes_recipepack')

        # Deleting model 'PackArg'
        db.delete_table('recipes_packarg')


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
            'Meta': {'object_name': 'Level'},
            'desc': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'released': ('django.db.models.fields.DateTimeField', [], {})
        },
        'recipes.packarg': {
            'Meta': {'object_name': 'PackArg'},
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
            'recipe': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'occurrences'", 'to': "orm['recipes.Spec']"})
        },
        'recipes.sourcepack': {
            'Meta': {'object_name': 'SourcePack'},
            'download_url': ('django.db.models.fields.URLField', [], {'unique': 'True', 'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
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
            'Meta': {'object_name': 'Spec'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.SlugField', [], {'max_length': '200', 'db_index': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'atlases'", 'to': "orm['auth.User']"}),
            'spec': ('django.db.models.fields.TextField', [], {}),
            'spec_type': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['recipes']
