# -*-coding: UTF-8-*-

from django import forms

class BetaForm(forms.Form):
    series_label = forms.CharField(max_length=200, label='Texture pack name',
        help_text='for example, Martin’s Gardener Pack')
    pack_label = forms.CharField(max_length=200, label='Current version',
        help_text='Latest version number – for example, v1.2')
    series_home_url = forms.URLField(max_length=1000, required=False, label='Home page',
        help_text='URL of a dedicated home page for this pack, if there is one')
    series_forum_url = forms.URLField(max_length=1000, required=False, label='Forum thread',
        help_text='URL of a forum thread about this texture pack')
    pack_download_url = forms.URLField(max_length=1000, label='Download URL',
        help_text='URL to download the ZIP file')
    pack_released = forms.DateTimeField(required=False, label='Released',
        help_text='When this version of the pack was was released. Leave blank to use today’s date')

