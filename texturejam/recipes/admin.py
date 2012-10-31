
from texturejam.recipes.models import Level, Tag, Source, Release, Spec, Remix, PackArg
from django.contrib import admin

class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'label']
    prepopulated_fields = {'name': ('label',)}

class ReleaseInline(admin.TabularInline):
    model = Release
    extra = 1

class SourceAdmin(admin.ModelAdmin):
    inlines = [ReleaseInline]
    list_display = ['label', 'owner', 'created', 'modified']

class PackArgInline(admin.TabularInline):
    model=PackArg
    extra=1

class RemixAdmin(admin.ModelAdmin):
    inlines = [PackArgInline]
    list_display = ['label', 'owner', 'created', 'modified', 'withdrawn', 'withdrawn_reason']

class SpecAdmin(admin.ModelAdmin):
    list_display = ['name', 'label', 'owner', 'created', 'modified']
    prepopulated_fields = {'name': ('label',)}

class RecipeAdmin(admin.ModelAdmin):
    list_display = ['label', 'owner', 'created', 'modified']

admin.site.register(Level)
admin.site.register(Tag, TagAdmin)
admin.site.register(Source, SourceAdmin)
admin.site.register(Spec, SpecAdmin)
admin.site.register(Remix, RemixAdmin)