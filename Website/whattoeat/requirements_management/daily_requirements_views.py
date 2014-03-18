from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from whattoeat.requirements_management.utils import calculate_daily_requirements_from_profile
from whattoeat.requirements_management.views import edit_requirements_set
from whattoeat.utilities import build_user_args

__author__ = 'michael'

@login_required
def auto_calculate_requirements_fail(request):
    args = build_user_args(request)
    return render_to_response('user_pages/profile/requirements/calculate_requirements_fail.html',args)

@login_required
def auto_calculate_requirements_success(request):
    args = build_user_args(request)

    profile = args['profile']
    daily_requirements_set = profile.get_daily_requirements_set()

    args['requirements'] = daily_requirements_set
    return render_to_response('user_pages/profile/requirements/view_daily_requirements.html',args)

@login_required
def calculate_daily_requirements(request):
    success = calculate_daily_requirements_from_profile(request)
    if success:
        return HttpResponseRedirect('/user/requirements/auto_calculate_success/')
    else:
        return HttpResponseRedirect('/user/requirements/auto_calculate_fail/')

@login_required
def edit_daily_requirements(request):
    return edit_requirements_set(request,daily=True)

@login_required
def view_daily_requirements(request):
    args = build_user_args(request)
    args['requirements'] = request.user.profile.get_daily_requirements_set()
    return render_to_response('user_pages/profile/requirements/view_daily_requirements.html',args)

