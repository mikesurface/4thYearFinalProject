from crispy_forms.helper import FormHelper
from django import forms
from whattoeat.models import MealRequirementsSet

__author__ = 'michael'

class MealRequirementsSelectorForm(forms.Form):
    '''Form for selecting a meal profile to use in meal generation'''
    req_set = forms.ModelChoiceField(label='Choose a requirements set to use',
                                     queryset=MealRequirementsSet.objects.all(),
                                     empty_label=None) #only a placeholder, queryset must be
                                                                                #set in init method
    def __init__(self,*args,**kwargs):
        user = kwargs.pop('user',None)
        super(MealRequirementsSelectorForm,self).__init__(*args,**kwargs)
        req_sets = user.profile.get_all_meal_requirements_sets()
        self.fields['req_set'].queryset = req_sets
        self.helper = FormHelper()
        self.helper.form_tag = False

