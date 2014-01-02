from ast import literal_eval
from django.http.response import HttpResponseRedirect
from django.shortcuts import render_to_response
from django import forms
from django.forms.formsets import formset_factory
from django.template.context import RequestContext
from whattoeat.forms.meal_generation_prototype import IngredientSelectForm, RequirementsInputForm
from whattoeat.meals import MealGeneration
from whattoeat.meals.MealClasses import DefiniteNutrientRequirement, RestrictedNutrientRequirement, Ingredient, Quantity, Requirements


def meal_generation_prototype(request, numIngredients, numRequirements):
    #prototype meal generation implemented 24/11/2013
    numIngredients = int(numIngredients)
    numRequirements = int(numRequirements)

    IngredientsFormSet = formset_factory(IngredientSelectForm, extra=numIngredients)
    RequirementsFormSet = formset_factory(RequirementsInputForm, extra=numRequirements)

    if request.method.upper() == 'POST':
        ingredients_formset = IngredientsFormSet(request.POST, request.FILES, prefix='ingredients')
        requirements_formset = RequirementsFormSet(request.POST, request.FILES, prefix='requirements')

        if ingredients_formset.is_valid() and requirements_formset.is_valid():

            requirements = Requirements()
            ingredients = []

            for form in requirements_formset: #process requirements
                requirement_name = form.cleaned_data['requirement']
                val = int(form.cleaned_data['amount']) #amount required or threshold on restriction

                if (form.cleaned_data['restriction'] == '='):
                    error = int(form.cleaned_data['error_margin'])
                    requirements.add(requirement_name, DefiniteNutrientRequirement(val=val, error=error))
                else:
                    restriction = form.cleaned_data['restriction']
                    requirements.add(requirement_name,
                                     RestrictedNutrientRequirement(threshold=val, restriction=restriction))

            nutrient_vals = {"chicken": {"calories": 2.19, "protein": 0.25, "fat": 0.13},
                             "pasta": {"calories": 3.71, "protein": 0.13, "carbs": 0.75, "fat": 0.015},
                             "oil": {"calories": 8.84, "fat": 1}}
            for form in ingredients_formset: # process ingredients
                name = form.cleaned_data["ingredient"].lower()
                values = nutrient_vals.get(form.cleaned_data["ingredient"]) #nutrient values of food
                quantity = int(form.cleaned_data["quantity"])
                unit = form.cleaned_data["unit"]
                fixed = bool(form.cleaned_data["fixed"])
                ingredients.append(
                    Ingredient(name=name, nutrient_values=values, quantity=quantity, unit=unit, fixed=fixed))

            quantities = MealGeneration.generate(ingredients, requirements)

            #######debug########
            f = open("output", 'a')
            f.write("AT VIEW\n")
            f.write(str(quantities) + "\n")
            f.write("Ingredients: \n")
            for ingredient in ingredients:
                f.write(str(ingredient) + "\n")
            for req in requirements.to_array():
                f.write(str(req) + "\n")
                ########debug#########

            quantity_of_ingredients = []
            for i in range(0, len(quantities)):
                quantity_of_ingredients.append(
                    Quantity(name=ingredients[i].name, quantity=quantities[i], unit=ingredients[i].unit))

            return render_to_response("prototype/meal_generator_form_output.html",
                                      {"quantities": quantity_of_ingredients}, context_instance=RequestContext(request))
    else:
        ingredients_formset = IngredientsFormSet(prefix='ingredients')
        requirements_formset = RequirementsFormSet(prefix='requirements')

    return render_to_response("meal_pages/meal_generation/meal_generation.html", {
        'requirements_formset': requirements_formset,
        'ingredients_formset': ingredients_formset,
    }, context_instance=RequestContext(request))