from django.core.context_processors import csrf
from django.shortcuts import render_to_response
from whattoeat.meals.Formulae import calculate_calories_per_day, daily_protein, daily_carbs, daily_fat, default_max_salt_grams, default_min_fibre_grams, daily_sugar, daily_satfat, default_error_margin
from whattoeat.models import DailyRequirementsSet, DefiniteDietRequirement, RestrictedDietRequirement
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
        DefiniteDietRequirement.objects.filter(set=req_set).delete()
        RestrictedDietRequirement.objects.filter(set=req_set).delete()
        req_set.delete()
        return True

    except Exception:
        return False


def collate_definite_requirements(requirements_set):
    definite_reqs = DefiniteDietRequirement.objects.filter(set=requirements_set)
    reqs = {}
    for r in definite_reqs:
        reqs[r.name.lower()] = r
    return reqs

def collate_restricted_requirements(requirements_set):
    restricted_reqs = RestrictedDietRequirement.objects.filter(set=requirements_set)
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

    daily_requirements_set = DailyRequirementsSet.objects.filter(profile=user.profile)[0]
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


        #delete exisiting requirements
        clear_daily_requirements(user)


        #put these into a requirements set
        #instantiate daily requirements set
        daily_requirements = DailyRequirementsSet(profile=profile,num_meals_per_day=num_meals_per_day)
        daily_requirements.save()


        try:
            DefiniteDietRequirement.objects.filter(set=daily_requirements).delete()
            RestrictedDietRequirement.onjects.filter(set=daily_requirements).delete()
        except Exception:
            pass #no data found

        #build each requirement
        calorie_requirement = DefiniteDietRequirement(set=daily_requirements,
                                                      name="Calories",
                                                      value = daily_calories,
                                                      error = error_margin)
        protein_requirement = DefiniteDietRequirement(set=daily_requirements,
                                                      name="Protein",
                                                      value=protein,
                                                      error= error_margin)
        carbs_requirement = DefiniteDietRequirement(set=daily_requirements,
                                                    name="Carbohydrate",
                                                    value=carbs,
                                                    error= error_margin)
        fat_requirement = DefiniteDietRequirement(set=daily_requirements,
                                                  name="Fat",
                                                  value=fat,
                                                  error= error_margin)
        salt_requirement = RestrictedDietRequirement(set=daily_requirements,
                                                     name="salt",
                                                     value=salt,
                                                     restriction='<=')
        fibre_requirement = RestrictedDietRequirement(set=daily_requirements,
                                                      name="fibre",
                                                      value = fibre,
                                                      restriction = '>=')
        sugar_requirement = RestrictedDietRequirement(set=daily_requirements,
                                                      name="sugar",
                                                      value = sugar,
                                                      restriction = '<=')
        satfat_requirement = RestrictedDietRequirement(set=daily_requirements,
                                                       name="satfat",
                                                       value = satfat,
                                                       restriction = '<=')

        #save requirements to requirements set
        calorie_requirement.save()
        protein_requirement.save()
        carbs_requirement.save()
        fat_requirement.save()
        salt_requirement.save()
        fibre_requirement.save()
        sugar_requirement.save()
        satfat_requirement.save()

        return True
    else:
        return False
