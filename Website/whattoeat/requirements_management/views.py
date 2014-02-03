from django.contrib.auth.decorators import login_required
from django.forms.models import modelformset_factory
from django.http.response import HttpResponseRedirect
from django.shortcuts import render_to_response
from whattoeat.requirements_management.forms import DefiniteRequirementForm, RestrictedRequirementForm, MealRequirementsSetForm, DailyRequirementsSetForm
from whattoeat.models import DefiniteDietRequirement, RestrictedDietRequirement
from whattoeat.utilities import build_user_args, build_user_args_for_form


@login_required
def edit_requirements_set(request, daily=False, name=""):
    args = build_user_args_for_form(request)
    profile = args['profile']

    if daily:
        args['daily'] = True

    args['edit_mode'] = True #tells the template we are editing, not adding
    args['req_set_name'] = name

    #define formsets
    DefiniteRequirementFormSet = modelformset_factory(DefiniteDietRequirement, form=DefiniteRequirementForm, extra=1)
    RestrictedRequirementFormSet = modelformset_factory(RestrictedDietRequirement, form=RestrictedRequirementForm,
                                                        extra=1)

    #data submitted
    if request.method.upper() == "POST":
        #collect form data
        if daily:
            req_set_form = DailyRequirementsSetForm(request.POST)
        else:
            req_set_form = MealRequirementsSetForm(request.POST)

        def_req_formset = DefiniteRequirementFormSet(request.POST, request.FILES, prefix="definite")
        res_req_formset = RestrictedRequirementFormSet(request.POST, request.FILES, prefix="restricted")

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
                try:
                    name = form.cleaned_data['name']
                    value = form.cleaned_data['value']
                    error = form.cleaned_data['error']
                    req_set.add_definite_requirement(name, value, error)
                except KeyError:
                    #empty form not removed
                    pass

            #add restricted requirements
            for form in res_req_formset:
                try:
                    name = form.cleaned_data['name']
                    value = form.cleaned_data['value']
                    restriction = form.cleaned_data['restriction']
                    req_set.add_restricted_requirement(name, value, restriction)
                except KeyError:
                    pass

            return HttpResponseRedirect('/user/requirements/update_requirements_success/')

        #return form, its not valid
        else:
            args['req_set_form'] = req_set_form
            args['def_req_formset'] = def_req_formset
            args['res_req_formset'] = res_req_formset
            return render_to_response('user_pages/profile/requirements/meal_profile_edit.html', args)


    ###Not Posted, render page
    if daily:
        #fetch the daily requirements
        req_set = profile.get_daily_requirements_set()
        req_set_form = DailyRequirementsSetForm(instance=req_set)
    else:
        #fetch meal requirements
        req_set = profile.get_meal_requirements_set(name=name)
        if req_set:
            req_set_form = MealRequirementsSetForm(instance=req_set)
        else:
            #new requirements set, follows there are no requirments attached
            req_set_form = MealRequirementsSetForm()


    #add set as a form
    args['req_set_form'] = req_set_form

    #fetch all requirements attached to this profile and use them to initialise appropriate forms


    def_reqs = req_set.get_all_definite_requirements()
    res_reqs = req_set.get_all_restricted_requirements()


    #definite requirements
    if def_reqs:
        def_req_formset = DefiniteRequirementFormSet(queryset=def_reqs, prefix="definite")
    else:
        #no def requirements
        def_req_formset = DefiniteRequirementFormSet(prefix="definite",queryset=DefiniteDietRequirement.objects.none())

    args['def_req_formset'] = def_req_formset

    #restricted requirements

    if res_reqs:
        res_req_formset = RestrictedRequirementFormSet(queryset=res_reqs, prefix="restricted")
    else:
        #no restricted requirements
        res_req_formset = RestrictedRequirementFormSet(prefix="restricted",
                                                       queryset=RestrictedDietRequirement.objects.none())
    args['res_req_formset'] = res_req_formset

    return render_to_response('user_pages/profile/requirements/meal_profile_edit.html', args)


@login_required()
def add_meal_requirements_set(request):
    args = build_user_args_for_form(request)
    profile = args['profile']
    #define formsets
    DefiniteRequirementFormSet = modelformset_factory(DefiniteDietRequirement, form=DefiniteRequirementForm, extra=1)
    RestrictedRequirementFormSet = modelformset_factory(RestrictedDietRequirement, form=RestrictedRequirementForm,
                                                        extra=1)

    if request.method.upper() == 'POST':
        req_set_form = MealRequirementsSetForm(request.POST)
        def_req_formset = DefiniteRequirementFormSet(request.POST, request.FILES, prefix="definite")
        res_req_formset = RestrictedRequirementFormSet(request.POST, request.FILES, prefix="restricted")


        #form input is valid
        if req_set_form.is_valid() and def_req_formset.is_valid() and res_req_formset.is_valid():
            #add meal requirements profile
            req_set = profile.add_meal_requirements_set(req_set_form.cleaned_data['name'])
            #clear old requirements
            req_set.clear_requirements()

            #add definite requirements
            for form in def_req_formset:
                try:
                    name = form.cleaned_data['name']
                    value = form.cleaned_data['value']
                    error = form.cleaned_data['error']
                    req_set.add_definite_requirement(name, value, error)
                except KeyError:
                    #empty form or some data was not entered
                    pass

            #add restricted requirements
            for form in res_req_formset:
                try:
                    name = form.cleaned_data['name']
                    value = form.cleaned_data['value']
                    restriction = form.cleaned_data['restriction']
                    req_set.add_restricted_requirement(name, value, restriction)
                except KeyError:
                    pass

            return HttpResponseRedirect('/user/requirements/my_meal_requirements/')

        else:
            #forms not valid
            args['req_set_form'] = req_set_form
            args['def_req_formset'] = def_req_formset
            args['res_req_formset'] = res_req_formset

        return render_to_response('user_pages/profile/requirements/meal_profile_edit.html', args)

    else:
        #new requirements set, follows there are no requirments attached
        #have to explicitly set the querysets to none for the corresponding table (otherwise it shows every row in the
        #underlying table)
        req_set_form = MealRequirementsSetForm()
        def_req_formset = DefiniteRequirementFormSet(prefix="definite",
                                                     queryset=DefiniteDietRequirement.objects.none())
        res_req_formset = RestrictedRequirementFormSet(prefix="restricted",
                                                       queryset=RestrictedDietRequirement.objects.none())

        args['req_set_form'] = req_set_form
        args['def_req_formset'] = def_req_formset
        args['res_req_formset'] = res_req_formset

        return render_to_response('user_pages/profile/requirements/meal_profile_edit.html', args)


@login_required()
def update_requirements_success(request):
    args = build_user_args(request)
    return render_to_response('user_pages/profile/requirements/requirements_update_success.html', args)


def recalculate_base_meal_set(request):
    args = build_user_args(request)
    profile = args['profile']
    daily_req_set = profile.get_daily_requirements_set()

    daily_calories = daily_req_set.get_requirement_by_name('calories')
    daily_protein = daily_req_set.get_requirement_by_name('protein')
    daily_carbs = daily_req_set.get_requirement_by_name('carbs')
    daily_fat = daily_req_set.get_requirement_by_name('fat')
    daily_satfat = daily_req_set.get_requirement_by_name('satfat')
    daily_fibre = daily_req_set.get_requirement_by_name('fibre')
    daily_salt = daily_req_set.get_requirement_by_name('salt')
    daily_sugar = daily_req_set.get_requirement_by_name('sugar')

    num_meals_per_day = daily_req_set.num_meals_per_day

    #build meal profile to match daily requirements
    profile.add_meal_requirements_set("Derived from Daily Requirements")
    meal_set = profile.get_meal_requirements_set("Derived from Daily Requirements")

    if daily_calories != None:
        if isinstance(daily_calories,DefiniteDietRequirement):
            meal_set.add_definite_requirement(nutrient_name="calories",
                                              value = daily_calories.value/num_meals_per_day,
                                              error = daily_calories.error)
        else:
            meal_set.add_restricted_requirement(nutrient_name='calories',
                                              value=daily_calories.value/num_meals_per_day,
                                              restriction=daily_calories.restriction)

    if daily_protein != None:
        if isinstance(daily_protein,DefiniteDietRequirement):
            meal_set.add_definite_requirement(nutrient_name="protein",
                                              value = daily_protein.value/num_meals_per_day,
                                              error = daily_protein.error)
        else:
            meal_set.add_restricted_requirement(nutrient_name='protein',
                                              value=daily_protein.value/num_meals_per_day,
                                              restriction=daily_protein.restriction)

    if daily_carbs != None:
        if isinstance(daily_carbs,DefiniteDietRequirement):
            meal_set.add_definite_requirement(nutrient_name="carbs",
                                              value = daily_carbs.value/num_meals_per_day,
                                              error = daily_carbs.error)
        else:
            meal_set.add_restricted_requirement(nutrient_name='carbs',
                                              value=daily_carbs.value/num_meals_per_day,
                                              restriction=daily_carbs.restriction)
    if daily_carbs != None:
        if isinstance(daily_fat,DefiniteDietRequirement):
            meal_set.add_definite_requirement(nutrient_name="fat",
                                              value = daily_fat.value/num_meals_per_day,
                                              error = daily_fat.error)
        else:
            meal_set.add_restricted_requirement(nutrient_name='fat',
                                              value=daily_fat.value/num_meals_per_day,
                                              restriction=daily_fat.restriction)
    if daily_satfat != None:
        if isinstance(daily_satfat,DefiniteDietRequirement):
            meal_set.add_definite_requirement(nutrient_name="satfat",
                                              value = daily_satfat.value/num_meals_per_day,
                                              error = daily_satfat.error)
        else:
            meal_set.add_restricted_requirement(nutrient_name='satfat',
                                              value=daily_satfat.value/num_meals_per_day,
                                              restriction=daily_satfat.restriction)
    if daily_fibre != None:
        if isinstance(daily_fibre,DefiniteDietRequirement):
            meal_set.add_definite_requirement(nutrient_name="fibre",
                                              value = daily_fibre.value/num_meals_per_day,
                                              error = daily_fibre.error)
        else:
            meal_set.add_restricted_requirement(nutrient_name='fibre',
                                              value=daily_fibre.value/num_meals_per_day,
                                              restriction=daily_fibre.restriction)

    if daily_salt != None:
        if isinstance(daily_salt,DefiniteDietRequirement):
            meal_set.add_definite_requirement(nutrient_name="salt",
                                              value = daily_salt.value/num_meals_per_day,
                                              error = daily_salt.error)
        else:
            meal_set.add_restricted_requirement(nutrient_name='salt',
                                              value=daily_salt.value/num_meals_per_day,
                                              restriction=daily_salt.restriction)
    if daily_sugar != None:
        if isinstance(daily_sugar,DefiniteDietRequirement):
            meal_set.add_definite_requirement(nutrient_name="sugar",
                                              value = daily_sugar.value/num_meals_per_day,
                                              error = daily_sugar.error)
        else:
            meal_set.add_restricted_requirement(nutrient_name='sugar',
                                              value=daily_sugar.value/num_meals_per_day,
                                              restriction=daily_sugar.restriction)

    return HttpResponseRedirect('/user/requirements/update_requirements_success/')