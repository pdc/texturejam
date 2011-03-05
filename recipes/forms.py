# -*-coding: UTF-8-*-

from django import forms

class BetaForm(forms.Form):
    pack_download_url = forms.URLField(max_length=1000, label='Download URL',
        help_text='URL to download the ZIP file')
    series_forum_url = forms.URLField(max_length=1000, required=False, label='Forum thread',
        help_text='URL of a forum thread about this texture pack')
    series_home_url = forms.URLField(max_length=1000, required=False, label='Home page',
        help_text='URL of a dedicated home page for this pack, if any')

