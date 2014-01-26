from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponseRedirect
from django.shortcuts import render_to_response
from whattoeat.requirements_management.views import edit_requirements_set
from whattoeat.utilities import build_user_args

__author__ = 'michael'

@login_required()
def view_meal_requirements(request):
    args = build_user_args(request)
    meal_sets = request.user.profile.get_all_meal_requirements_sets()
    args['meal_sets'] = meal_sets
    return render_to_response('user_pages/profile/requirements/meal_sets/manage_meal_sets.html',args)


@login_required
def edit_meal_requirements(request,name):
    return edit_requirements_set(request,name=name)

@login_required
def add_meal_requirements(request):
    return edit_requirements_set(request)

@login_required()
def remove_meal_set(request,name):
    args=build_user_args(request)
    profile = args['profile']
    profile.delete_meal_requirements_set(name)
    return HttpResponseRedirect('/user/requirements/my_meal_requirements/')
