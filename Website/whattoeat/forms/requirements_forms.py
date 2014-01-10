from django import forms
from django.forms.widgets import TextInput

__author__ = 'michael'

class PercentageInput(TextInput):
    input_type = 'number'
    step = 1


class DailyRequirementsByRatiosForm(forms.Form):
    protein = forms.IntegerField(widget=PercentageInput,min_value=0,max_value=100)
    carbs = forms.IntegerField(widget=PercentageInput,min_value=0,max_value=100)
    fat = forms.IntegerField(widget=PercentageInput,min_value=0,max_value=100)
