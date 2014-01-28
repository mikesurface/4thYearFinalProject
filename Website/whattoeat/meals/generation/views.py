from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from whattoeat.meals.ingredient_search.forms import FoodSearchFormCompressed
from whattoeat.utilities import build_user_args

@login_required()
def meal_generation(request):
    args = build_user_args(request)
    args['ingredients_search_form'] = FoodSearchFormCompressed()
    return render_to_response('meal_pages/generation/meal_generation.html',args)
