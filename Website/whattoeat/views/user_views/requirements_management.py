from django.core.context_processors import csrf
from django.forms.models import modelformset_factory
from django.http.response import HttpResponseRedirect
from django.shortcuts import render_to_response
from whattoeat.forms.requirements_forms import DefiniteRequirementForm, RestrictedRequirementForm, MealRequirementsSetForm, DailyRequirementsSetForm
from whattoeat.meals.Formulae import calculate_calories_per_day, daily_protein, daily_carbs, daily_fat, default_max_salt_grams, default_min_fibre_grams, daily_sugar, daily_satfat, default_error_margin
from whattoeat.models import DailyRequirementsSet, DefiniteDietRequirement, RestrictedDietRequirement, MealRequirementsSet
from whattoeat.shared_views import check_user_logged_in


'''
Clear the daily requirements set up for the uer from the database
Returns True if requirements were cleared
False if clearing failed or no requirements exisited
'''
def clear_daily_requirements(user):
    profile = user.profile
    try:
        req_set = DailyRequirementsSet.objects.filter(profile=profile)
        DefiniteDietRequirement.objects.filter(content_type=req_set).delete()
        RestrictedDietRequirement.objects.filter(content_type=req_set).delete()
        req_set.delete()
        return True

    except Exception:
        return False


def collate_definite_requirements(requirements_set):
    definite_reqs = requirements_set.get_all_definite_requirements()
    reqs = {}
    for r in definite_reqs:
        reqs[r.name.lower()] = r
    return reqs

def collate_restricted_requirements(requirements_set):
    restricted_reqs = requirements_set.get_all_restricted_requirements()
    reqs={}
    for r in restricted_reqs:
        reqs[r.name.lower()] = r
    return reqs

def auto_calculate_requirements_fail(request):
    check_user_logged_in(request)
    user = request.user
    args = {'user':user}
    return render_to_response('user_pages/profile/requirements/calculate_requirements_fail.html',args)

def auto_calculate_requirements_success(request):
    check_user_logged_in(request)
    user = request.user
    profile = user.profile

    daily_requirements_set = profile.get_daily_requirements_set()
    definite_requirements = collate_definite_requirements(daily_requirements_set)
    restricted_requirements = collate_restricted_requirements(daily_requirements_set)

    args={'user':user}
    args['definite_requirements'] = definite_requirements
    args['restricted_requirements'] = restricted_requirements
    args['num_meals_per_day'] = daily_requirements_set.num_meals_per_day

    return render_to_response('user_pages/profile/requirements/calculate_requirements_success.html',args)


def calculate_daily_requirements_from_profile(request):
    user = request.user
    profile = user.profile
    gender = profile.gender
    age = profile.age
    height = profile.height
    weight = profile.weight
    goal = profile.goal

    #check that none of these fields are empty, as this will raise exceptions
    if gender and age and height and weight and goal:
        #calculate recommended base daily requirements
        daily_calories = calculate_calories_per_day(height,weight,age,gender,goal)
        protein = daily_protein(daily_calories)
        carbs = daily_carbs(daily_calories)
        fat = daily_fat(daily_calories)
        salt = default_max_salt_grams()
        fibre = default_min_fibre_grams()
        sugar = daily_sugar(daily_calories)
        satfat = daily_satfat(daily_calories)
        num_meals_per_day = 3
        error_margin = default_error_margin()

        #create a daily requirements set (or overwrite exisiting one)
        profile.add_daily_requirements_set(num_meals_per_day)
        daily_requirements = profile.get_daily_requirements_set()

        #build each requirement
        #note the name MUST MAP to the choices in the models form or retrieval will not work
        daily_requirements.add_definite_requirement(nutrient_name="calories",
                                                      value = daily_calories,
                                                      error = error_margin)

        daily_requirements.add_definite_requirement(nutrient_name="protein",
                                                      value = protein,
                                                      error = error_margin)

        daily_requirements.add_definite_requirement(nutrient_name="carbs",
                                                    value = carbs,
                                                      error = error_margin)

        daily_requirements.add_definite_requirement(nutrient_name="fat",
                                                      value = fat,
                                                      error = error_margin)

        daily_requirements.add_restricted_requirement(nutrient_name="salt",
                                                      value = salt,
                                                      restriction="<=")

        daily_requirements.add_restricted_requirement(nutrient_name="satfat",
                                                      value = satfat,
                                                      restriction="<=")

        daily_requirements.add_restricted_requirement(nutrient_name="sugar",
                                                      value = sugar,
                                                      restriction="<=")

        daily_requirements.add_restricted_requirement(nutrient_name="fibre",
                                                      value = fibre,
                                                      restriction=">=")


        return True
    else:
        return False

def edit_daily_requirements(request):
    check_user_logged_in(request)
    user = request.user
    profile = user.profile
    args = {'user':user,'daily':True}
    args.update(csrf(request)) #update csrf token

    #define formsets
    DefiniteRequirementFormSet = modelformset_factory(DefiniteDietRequirement,form=DefiniteRequirementForm)
    RestrictedRequirementFormSet = modelformset_factory(RestrictedDietRequirement,form=RestrictedRequirementForm)

    #data submitted
    if request.method.upper() == "POST":
        #collect form data
        req_set_form = DailyRequirementsSetForm(request.POST)
        def_req_formset = DefiniteRequirementFormSet(request.POST,request.FILES,prefix="definite")
        res_req_formset = RestrictedRequirementFormSet(request.POST,request.FILES,prefix="restricted")

        #form input is valid
        if req_set_form.is_valid() and def_req_formset.is_valid() and res_req_formset.is_valid():
            #update daily requirements profile
            profile.add_daily_requirements_set(req_set_form.cleaned_data['num_meals_per_day'])
            req_set = profile.get_daily_requirements_set()

            #clear old requiremetnts
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

            return HttpResponseRedirect('/user/profile/requirements/edit_requirements_success/')

        #return form, its not valid
        else:
            args['req_set_form'] = req_set_form
            args['def_req_formset'] = def_req_formset
            args['res_req_formset'] = res_req_formset
            return render_to_response('user_pages/profile/requirements/meal_profile_edit.html',args)

    #fetch the daily requirements

    req_set =  profile.get_daily_requirements_set()
    req_set_form = DailyRequirementsSetForm(instance= req_set)


    #add profile as a form
    args['req_set_form'] = req_set_form


    #fetch all requirements attached to this profile and use them to initialise appropriate forms
    #definite requirements

    try:
        def_reqs = req_set.get_all_definite_requirements()
        def_req_formset = DefiniteRequirementFormSet(queryset=def_reqs,prefix="definite")
    except BaseException:
        #no def requirements or DB error
        def_req_formset = DefiniteRequirementFormSet()
    args['def_req_formset'] = def_req_formset

    #restricted requirements
    try:
        res_reqs =  req_set.get_all_restricted_requirements()
        res_req_formset = RestrictedRequirementFormSet(queryset=res_reqs,prefix="restricted")
    except BaseException:
        #no res requirements or DB error
        res_req_formset = RestrictedRequirementFormSet()
    args['res_req_formset'] = res_req_formset

    return render_to_response('user_pages/profile/requirements/meal_profile_edit.html',args)



def edit_requirements_success(request):
    check_user_logged_in(request)
    user = request.user
    args = {'user':user}
    return render_to_response('user_pages/profile/requirements/meal_profile_edit_success.html',args)


def add_meal_requirements_set(request,name):
    check_user_logged_in(request)
    user=request.user
    profile = user.profile
    args={'user':user}

    result = profile.add_meal_requirements_set

