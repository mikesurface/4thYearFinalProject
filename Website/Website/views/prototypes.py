from django.shortcuts import render_to_response
from django import forms
from django.forms.formsets import formset_factory
from Website.forms.meal_generation_prototype import IngredientSelectForm, RequirementsInputForm


def meal_generation_prototype(request, numIngredients, numRequirements):
    #prototype meal generation implemented 24/11/2013

    IngredientsFormSet = formset_factory(IngredientSelectForm, extra=numIngredients)
    RequirementsFormSet = formset_factory(RequirementsInputForm, extra=numRequirements)
    if request.method == 'POST':
        ingredients_formset = IngredientsFormSet(request.POST, request.FILES, prefix='ingredients')
        requirements_formset = RequirementsFormSet(request.POST, request.FILES, prefix='requirements')
        if ingredients_formset.is_valid() and requirements_formset.is_valid():
            for form in ingredients_formset:
                print form.clean_data['ingredient']
            for form in requirements_formset:
                print form.clean_data['requirement']
    else:
        ingredients_formset = IngredientsFormSet( prefix='ingredients')
        requirements_formset = RequirementsFormSet( prefix='requirements')
    return render_to_response("meal_pages/meal_generation.html",
                              {'requirements_formset': requirements_formset,
                              'ingredients_formset': ingredients_formset,
                              })