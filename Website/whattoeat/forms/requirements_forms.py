from django import forms
from whattoeat.models import DefiniteDietRequirement, RestrictedDietRequirement, DailyRequirementsSet, MealRequirementsSet


class DailyRequirementsSetForm(forms.ModelForm):
    num_meals_per_day = forms.IntegerField(widget=forms.NumberInput({'step':1,'max':8,'min':1}))
    
    class Meta:
        model = DailyRequirementsSet
        fields = ("num_meals_per_day",)

class MealRequirementsSetForm(forms.ModelForm):
    class Meta:
        model = MealRequirementsSet
        fields = ("name",)

class DefiniteRequirementForm(forms.ModelForm):
     id = forms.IntegerField(widget=forms.HiddenInput())
     class Meta:
         model = DefiniteDietRequirement
         fields = ("id","name","value","error")
         #note id is required as it this form will be used in a ModelFormSet (see Django Docs)

class RestrictedRequirementForm(forms.ModelForm):
    id = forms.IntegerField(widget=forms.HiddenInput())
    class Meta:
        model = RestrictedDietRequirement
        fields = ("id","name","value","restriction")
        #note id is required as it this form will be used in a ModelFormSet (see Django Docs)