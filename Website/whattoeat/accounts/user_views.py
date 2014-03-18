from django.contrib.auth.decorators import login_required
from django.core.context_processors import csrf
from django.http.response import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from whattoeat.accounts.forms import DietProfileForm
from whattoeat.solver_backend import UnitConversions
from whattoeat.utilities import build_user_args_for_form


def user_homepage(request):
    args = build_user_args_for_form(request)
    return render_to_response('user_pages/profile/user_page/user_page.html',args,context_instance=RequestContext(request))

@login_required
def edit_diet_profile(request):
    #check user is logged in
    args=build_user_args_for_form(request)

    if request.method.upper() == 'POST':
        stats_form = DietProfileForm(request.POST,instance=request.user.profile)

        #form is valid
        if stats_form.is_valid():
            profile = stats_form.save()

            #save info
            profile.save()

            #if the user wants to save and quit, redirect to home page and do nothing
            #if they want to recalculate their daily requirements,do so then take them to a page confirming them
            if 'calculate' in request.POST:
                return HttpResponseRedirect('/user/requirements/auto_calculate/')
            else:
                return HttpResponseRedirect('/user/')

        #error in form data (invalid form)
        else:
            args['stats_form'] = stats_form

    #no form submitted: render page
    else:
        stats_form = DietProfileForm(instance=request.user.profile)
        args['stats_form'] = stats_form

    #first visit or invalid form data
    return render_to_response('user_pages/profile/edit_stats.html',args)


