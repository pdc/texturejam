# -*-coding: UTF-8-*-

"""Template Context Processors for authentication & profile stiff,
"""

from models import *

def profile(request):
    """Ensure the user's profile is added to the template context."""
    result = {}
    if request.user.is_authenticated():
        result['user_profile'] = create_profile_if_missing(request.user)
    return result