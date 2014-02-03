from whattoeat.solver_backend.Formulae import calculate_calories_per_day, daily_protein, daily_carbs, daily_fat, default_min_fibre_grams, daily_sugar, default_max_salt_grams, daily_satfat, default_error_margin

__author__ = 'michael'

def collate_definite_requirements(requirements_set):
    '''
    Gather together the definite requirements, putting them into a dictionary mapping the nutrient name
    to the requirement
    '''
    definite_reqs = requirements_set.get_all_definite_requirements()
    reqs = {}
    for r in definite_reqs:
        reqs[r.name.lower()] = r
    return reqs

def collate_restricted_requirements(requirements_set):
    '''
    Gather together the restricted requirements, putting them into a dictionary mapping the nutrient name
    to the requirement
    '''
    restricted_reqs = requirements_set.get_all_restricted_requirements()
    reqs={}
    for r in restricted_reqs:
        reqs[r.name.lower()] = r
    return reqs

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

        #build meal profile to match daily requirements
        profile.add_meal_requirements_set("Derived from Daily Requirements")
        meal_set = profile.get_meal_requirements_set("Derived from Daily Requirements")
        meal_set.add_definite_requirement(nutrient_name="calories",
                                                      value = daily_calories/num_meals_per_day,
                                                      error = error_margin)

        meal_set.add_definite_requirement(nutrient_name="protein",
                                                      value = protein/num_meals_per_day,
                                                      error = error_margin)

        meal_set.add_definite_requirement(nutrient_name="carbs",
                                                    value = carbs/num_meals_per_day,
                                                      error = error_margin)

        meal_set.add_definite_requirement(nutrient_name="fat",
                                                      value = fat/num_meals_per_day,
                                                      error = error_margin)

        meal_set.add_restricted_requirement(nutrient_name="salt",
                                                      value = salt/num_meals_per_day,
                                                      restriction="<=")

        meal_set.add_restricted_requirement(nutrient_name="satfat",
                                                      value = satfat/num_meals_per_day,
                                                      restriction="<=")

        meal_set.add_restricted_requirement(nutrient_name="sugar",
                                                      value = sugar/num_meals_per_day,
                                                      restriction="<=")

        meal_set.add_restricted_requirement(nutrient_name="fibre",
                                                      value = fibre/num_meals_per_day,
                                                      restriction=">=")




        return True
    else:
        return False