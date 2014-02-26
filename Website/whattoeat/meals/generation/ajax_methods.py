from django.http import HttpResponseBadRequest
from django.shortcuts import render_to_response
from whattoeat.meals.ingredient_search.forms import ServingForm, IngredientForm


def serving_to_ingredient_form(request):
    '''Takes in a serving form and turns it into an ingredient form, then returns the html to render the result'''
    if request.method.upper() == "GET":
        form = ServingForm(request.GET)
        if form.is_valid():
            data = form.cleaned_data
            form = IngredientForm(initial=data)
            args = {}
            args['ing_form'] = form
            args['food_name'] =  data['food_name']
            args['ing_desc'] = data['description']
            args['units'] = data['units']
            return render_to_response('meal_pages/generation/ingredient_form.html',args)

    return HttpResponseBadRequest()