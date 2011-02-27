
from recipes.models import Level, SourceSeries, SourcePack, Spec, RecipePack, PackArg
from django.contrib import admin

class SourcePackInline(admin.TabularInline):
    model=SourcePack
    extra=1

class SourceSeriesAdmin(admin.ModelAdmin):
    inlines = [SourcePackInline]
    list_display = ['label', 'owner', 'created', 'modified']

class PackArgInline(admin.TabularInline):
    model=PackArg
    extra=1

class RecipePackAdmin(admin.ModelAdmin):
    inlines = [PackArgInline]
    list_display = ['label', 'owner', 'created', 'modified']

class SpecAdmin(admin.ModelAdmin):
    list_display = ['name', 'label', 'owner', 'created', 'modified']
    prepopulated_fields = {'name': ('label',)}

class RecipeAdmin(admin.ModelAdmin):
    list_display = ['label', 'owner', 'created', 'modified']

admin.site.register(Level)
admin.site.register(SourceSeries, SourceSeriesAdmin)
admin.site.register(Spec, SpecAdmin)
admin.site.register(RecipePack, RecipePackAdmin)