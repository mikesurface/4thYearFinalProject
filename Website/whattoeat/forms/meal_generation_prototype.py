from django import forms

UNITS = (('oz','ounces'),('g','grams'))

RESTRICTIONS = (('=','equal to'),('<','less than'),('>','more than'),('>=','at least'),('<=','no more than'),)

class IngredientSelectForm(forms.Form):

    quantity = forms.IntegerField(min_value = 0)
    unit = forms.ChoiceField(choices=UNITS)
    fixed = forms.ChoiceField(choices=((True,"Yes"),(False,"N")))

class RequirementsInputForm(forms.Form):
    requirement = forms.CharField()
    restriction = forms.ChoiceField(choices=RESTRICTIONS)
    amount = forms.FloatField(min_value=0.0)
    error_margin = forms.FloatField(min_value=0.0)