from django.contrib.auth.decorators import login_required
from django.forms.formsets import formset_factory
from django.shortcuts import render_to_response
from whattoeat.meals.generation.forms import MealRequirementsSelectorForm
from whattoeat.meals.ingredient_search.forms import FoodSearchFormCompressed, IngredientForm
from whattoeat.solver_backend.MealClasses import Ingredient, RestrictedIngredient
from whattoeat.solver_backend.MealGeneration import MealGenerator
from whattoeat.utilities import build_user_args, build_user_args_for_form


@login_required()
def meal_generation(request):
    args = build_user_args_for_form(request)
    args['not_searched_yet'] = True #reset search on any action

    #we never read this forms contents since all work done through AJAX
    args['ingredients_search_form'] = FoodSearchFormCompressed()
    #define an ingredients formset. we never want initial forms because they must be created as the result of search
    IngredientsFormSet = formset_factory(IngredientForm,extra=0)

    if request.method.upper() == 'POST':
        #form form selecting a requirements set to us
        req_set_selector = MealRequirementsSelectorForm(request.POST,user=args['user'])
        #formset for ingredients in the meal
        ingredients_formset = IngredientsFormSet(request.POST,request.FILES,prefix="ingredients")

        args['meal_req_set_selector'] = MealRequirementsSelectorForm(user=args['user'])
        args['ingredients_formset'] = ingredients_formset
        args['generator_used'] = 'true' #tells javascript we havee attempted a generation

        if req_set_selector.is_valid() and ingredients_formset.is_valid():
            gen = MealGenerator() #meal generator
            req_set = req_set_selector.cleaned_data['req_set']
            #set the selected req set for returning the form so the page shows the req set used
            args['meal_req_set_selector'] = MealRequirementsSelectorForm(user=args['user'],selected=req_set)

            #build problem instance
            #definite requirements
            for def_req in req_set.get_all_definite_requirements():
                gen.add_definite_requirement(def_req.name,def_req.value,def_req.error)
            #restricted requirements
            for res_req in req_set.get_all_restricted_requirements():
                gen.add_restricted_requirement(res_req.name,res_req.value,res_req.restriction)

            #build ingredients
            for ing in ingredients_formset:
                data = ing.cleaned_data
                #get the nutrient data
                nutrient_vals = {}
                nutrient_vals['calories'] = float(data['calories'])
                nutrient_vals['protein'] = float(data['protein'])
                nutrient_vals['carbs'] = float(data['carbs'])
                nutrient_vals['fat'] = float(data['fat'])
                #note that all potentially missing data has been filled in with zeros where not found
                #so we can safely add them without checking
                nutrient_vals['salt'] = float(data['salt'])
                nutrient_vals['fibre'] = float(data['fibre'])
                nutrient_vals['sugar'] = float(data['sugar'])
                nutrient_vals['satfat'] = float(data['satfat'])

                #get other data
                name = data['food_name']
                food_id = data['food_id']
                serving_id = data['serving_id']

                #get quantity data: if metric data is available prefer this over non-metric
                if data['metric_quantity'] is not None and data['metric_units'] is not None:
                    quantity = data['metric_quantity']
                    units = data['metric_units']
                else:
                    quantity = data['quantity']
                    units = data['units']

                #check if the ingredient is restricted
                restriction = None
                threshold = None
                if data['restriction'] != 'None':#note None is a string here as it came from the form
                    restriction = data['restriction']
                if data['threshold'] != None:
                        threshold = data['threshold']

                #check if fixed
                fixed = data['fixed']

                #build ingredient
                if restriction != None and threshold != None:
                     ingredient = RestrictedIngredient(name,quantity,units,threshold,restriction=restriction,
                                                     nutrient_values=nutrient_vals,fixed=fixed)
                else:
                    ingredient = Ingredient(name,quantity,units,nutrient_values=nutrient_vals,fixed=fixed)

                gen.add_ingredient(ingredient)

            #solve
            result = gen.generate(True)
            #if a solution exists,break it down
            if result:
                #turn quantities into a recipe format
                raw_quants = result['quantities']
                for n in raw_quants:
                    pass
                args['content'] = result['content']
                return render_to_response('meal_pages/generation/meal_generation.html',args)
            else:
                args['no_solution'] = True
                return render_to_response('meal_pages/generation/meal_generation.html',args)

        else:
            return render_to_response('meal_pages/generation/meal_generation.html',args)

    else:
        #just display the page, nothing done yet
        args['ingredients_search_form'] = FoodSearchFormCompressed()
        args['not_searched_yet'] = True
        args['generator_used'] = 'false' #must be a string as this is passed to javascript
        args['meal_req_set_selector'] = MealRequirementsSelectorForm(user=args['user'])
        ingredients_formset = IngredientsFormSet(prefix="ingredients",)
        args['ingredients_formset'] = ingredients_formset
        return render_to_response('meal_pages/generation/meal_generation.html',args)

