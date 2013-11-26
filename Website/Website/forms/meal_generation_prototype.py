from django import forms

INGREDIENTS = (['1g of Chicken',2.19,0.25,0,0.13],
               ['1g of Pasta',3.71,0.13,0.75,0.015],
               ['1g of Olive Oil',8.84,0,0,1],
)

RESTRICTIONS = ('equal to','less than','more than','at least','no more than')

class IngredientSelectForm(forms.Form):
    ingredient = forms.ChoiceField(choices = INGREDIENTS)

class RequirementsInputForm(forms.Form):
    requirement = forms.CharField()
    restriction = forms.ChoiceField(choices=RESTRICTIONS)
    amount = forms.FloatField(min_value=0.0)
    error = forms.FloatField(min_value=0.0)