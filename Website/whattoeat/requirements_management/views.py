from django.contrib.auth.decorators import login_required
from django.forms.models import modelformset_factory
from django.http.response import HttpResponseRedirect
from django.shortcuts import render_to_response
from whattoeat.requirements_management.forms import DefiniteRequirementForm, RestrictedRequirementForm, MealRequirementsSetForm, DailyRequirementsSetForm
from whattoeat.models import DefiniteDietRequirement, RestrictedDietRequirement
from whattoeat.requirements_management.utils import collate_restricted_requirements, collate_definite_requirements, calculate_daily_requirements_from_profile
from whattoeat.utilities import build_user_args, build_user_args_for_form


@login_required
def edit_requirements_set(request,daily=False,name=""):
    args = build_user_args_for_form(request)
    profile = args['profile']

    if daily:
        args['daily'] = True

    #define formsets
    DefiniteRequirementFormSet = modelformset_factory(DefiniteDietRequirement,form=DefiniteRequirementForm)
    RestrictedRequirementFormSet = modelformset_factory(RestrictedDietRequirement,form=RestrictedRequirementForm)

    #data submitted
    if request.method.upper() == "POST":
        #collect form data
        if daily:
            req_set_form = DailyRequirementsSetForm(request.POST)
        else:
            req_set_form = MealRequirementsSetForm(request.POST)

        def_req_formset = DefiniteRequirementFormSet(request.POST,request.FILES,prefix="definite")
        res_req_formset = RestrictedRequirementFormSet(request.POST,request.FILES,prefix="restricted")

        #form input is valid
        if req_set_form.is_valid() and def_req_formset.is_valid() and res_req_formset.is_valid():

            if daily:
                #update daily requirements profile
                req_set = profile.add_daily_requirements_set(req_set_form.cleaned_data['num_meals_per_day'])
            else:
                #update meal requirements profile
                req_set = profile.add_meal_requirements_set(req_set_form.cleaned_data['name'])

            #clear old requirements
            req_set.clear_requirements()

            #add definite requirements
            for form in def_req_formset:
                name = form.cleaned_data['name']
                value = form.cleaned_data['value']
                error = form.cleaned_data['error']
                req_set.add_definite_requirement(name,value,error)

            #add restricted requirements
            for form in res_req_formset:
                name = form.cleaned_data['name']
                value = form.cleaned_data['value']
                restriction = form.cleaned_data['restriction']
                req_set.add_restricted_requirement(name,value,restriction)

            return HttpResponseRedirect('/user/requirements/my_daily_requirements/')

        #return form, its not valid
        else:
            args['req_set_form'] = req_set_form
            args['def_req_formset'] = def_req_formset
            args['res_req_formset'] = res_req_formset
            return render_to_response('user_pages/profile/requirements/meal_profile_edit.html',args)


    ###Not Posted, render page
    if daily:
        #fetch the daily requirements
        req_set =  profile.get_daily_requirements_set()
        req_set_form = DailyRequirementsSetForm(instance= req_set)
    else:
        #fetch meal requirements
        req_set = profile.get_meal_requirements_set(name = name)
        if req_set:
            req_set_form = MealRequirementsSetForm(instance = req_set)
        else:
            #new requirements set, follows there are no requirments attached
            req_set_form = MealRequirementsSetForm()


    #add set as a form
    args['req_set_form'] = req_set_form

    #fetch all requirements attached to this profile and use them to initialise appropriate forms
    #definite requirements
    def_reqs = req_set.get_all_definite_requirements()
    if def_reqs:
        def_req_formset = DefiniteRequirementFormSet(queryset=def_reqs,prefix="definite")
    else:
        #no def requirements
        def_req_formset = DefiniteRequirementFormSet(prefix="definite")
    args['def_req_formset'] = def_req_formset

    #restricted requirements
    res_reqs =  req_set.get_all_restricted_requirements()
    if res_reqs:
        res_req_formset = RestrictedRequirementFormSet(queryset=res_reqs,prefix="restricted")
    else:
        #no restricted requirements
        res_req_formset = RestrictedRequirementFormSet(prefix="restricted")
    args['res_req_formset'] = res_req_formset

    return render_to_response('user_pages/profile/requirements/meal_profile_edit.html',args)




