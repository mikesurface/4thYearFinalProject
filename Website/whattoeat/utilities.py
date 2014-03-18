from django.core.context_processors import csrf
__author__ = 'michael'

DEFAULT_ADDITIONAL_MEAL_PROFILES = 4 #defines how many extra meal profiles the user may have (on top of the

def build_user_args(request):
    '''
    Instantiates an arguments dictionary for a template,
    containing the current user (key 'user') and their profile (key 'profile')
    Or returns an empty dictionary if the user is not logged in
    Note this DOES NOT check the user is logged in
    '''
    args = {}
    user = request.user
    if user.is_authenticated():
        args['user'] = request.user
        args['profile'] = request.user.profile
    return args

def build_user_args_for_form(request):
    '''
    Instantiates an arguments dictionary for a template and update the csrf token.
    containing the current user (key 'user') and their profile (key 'profile')
    Or returns an empty dictionary if the user is not logged in
    Note this DOES NOT check the user is logged in
    '''
    args = build_user_args(request)
    args.update(csrf(request))
    return args