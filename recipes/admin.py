
from recipes.models import Level, Tag, SourceSeries, SourcePack, Spec, RecipePack, PackArg
from django.contrib import admin

class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'label']
    prepopulated_fields = {'name': ('label',)}

class SourcePackInline(admin.TabularInline):
    model = SourcePack
    extra = 1

class SourceSeriesAdmin(admin.ModelAdmin):
    inlines = [SourcePackInline]
    list_display = ['label', 'owner', 'created', 'modified']

class PackArgInline(admin.TabularInline):
    model=PackArg
    extra=1

class RecipePackAdmin(admin.ModelAdmin):
    inlines = [PackArgInline]
    list_display = ['label', 'owner', 'created', 'modified', 'withdrawn', 'withdrawn_reason']

class SpecAdmin(admin.ModelAdmin):
    list_display = ['name', 'label', 'owner', 'created', 'modified']
    prepopulated_fields = {'name': ('label',)}

class RecipeAdmin(admin.ModelAdmin):
    list_display = ['label', 'owner', 'created', 'modified']

admin.site.register(Level)
admin.site.register(Tag, TagAdmin)
admin.site.register(SourceSeries, SourceSeriesAdmin)
admin.site.register(Spec, SpecAdmin)
admin.site.register(RecipePack, RecipePackAdmin)