from django.core.context_processors import csrf
from django.http.response import HttpResponseRedirect
from django.shortcuts import render_to_response, redirect
from whattoeat.forms.user_forms import DietProfileForm
from whattoeat.meals import UnitConversions
from whattoeat.shared_views import check_user_logged_in
from whattoeat.views.user_views.requirements_management import calculate_daily_requirements_from_profile


def user_homepage(request):
    check_user_logged_in(request)
    args = {}
    args['user'] = request.user
    return render_to_response('user_pages/profile/user_page.html',args)


def edit_diet_profile(request):
    #check user is logged in
    check_user_logged_in(request)
    if request.method.upper() == 'POST':
        stats_form = DietProfileForm(request.POST,instance=request.user.profile)
        height_units = request.POST.get('height_unit', 'cm')
        weight_units = request.POST.get('weight_unit', 'kg')

        #form is valid
        if stats_form.is_valid():
            profile = stats_form.save()

            #convert height to metres
            if height_units == 'inches':
                #convert inches to m
                profile.height = profile.height * UnitConversions.INCHES_TO_M
            else:
                #convert cm to m
                profile.height /= 100

            #convert weight to kg
            if weight_units == 'lbs':
                profile.weight *= UnitConversions.POUNDS_TO_KILOS

            #save info
            profile.save()

            #if the user wants to save and quit, redirect to home page and do nothing
            #if they want to recalculate their daily requirements,do so then take them to a page confirming them
            if 'calculate' in request.POST:
                success = calculate_daily_requirements_from_profile(request)
                if success:
                    return HttpResponseRedirect('/user/profile/requirements/auto_calculate_success/')
                else:
                    return HttpResponseRedirect('/user/profile/requirements/auto_calculate_fail/')


            return HttpResponseRedirect('/user/profile/')

        #error in form data (invalid form)
        else:
            args = {}
            args.update(csrf(request))
            args['stats_form'] = stats_form
            args['user'] = request.user
            return render_to_response('user_pages/profile/edit_stats.html',args)

    #no form submitted: render page
    else:
        user = request.user
        profile = user.profile
        stats_form = DietProfileForm(instance=profile)

        args = {}
        args.update(csrf(request))
        args['stats_form'] = stats_form
        args['user'] = user

        return render_to_response('user_pages/profile/edit_stats.html',args)


