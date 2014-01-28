from crispy_forms.bootstrap import FieldWithButtons
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div
from whattoeat.forms.custom_crispy_layouts import PlainSubmit
from django import forms


class FoodSearchForm(forms.Form):
    '''Form for ingredients search bar'''
    search_text = forms.CharField(
        initial="Enter search text",
        required=True,
        widget=forms.TextInput,
        min_length=1,
    )

    def __init__(self, *args, **kwargs):
        super(FoodSearchForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        helper = self.helper
        helper.form_method = "GET"
        helper.form_action = "."
        helper.form_show_labels = False
        helper.form_id = "ingredients_search_form"
        helper.layout = Layout(
           FieldWithButtons('search_text',PlainSubmit('search','Search',css_class="btn-success",css_id="ingredient_search_submit")),
        )

class FoodSearchFormCompressed(FoodSearchForm):
    '''Form for ingredients search using AJAX in compressed search'''
    def __init__(self,*args,**kwargs):
        super(FoodSearchFormCompressed, self).__init__(*args, **kwargs)
        self.helper.form_tag = False


class ServingForm(forms.Form):
    '''Form for displaying a serving of an ingredient, with info required to manipulate the ingredient further'''
    calories = forms.FloatField(widget=forms.HiddenInput())
    protein = forms.FloatField(widget=forms.HiddenInput())
    carbs = forms.FloatField(widget=forms.HiddenInput())
    fat = forms.FloatField(widget=forms.HiddenInput())
    salt = forms.FloatField(widget=forms.HiddenInput())
    sugar = forms.FloatField(widget=forms.HiddenInput())
    fibre = forms.FloatField(widget=forms.HiddenInput())
    satfat = forms.FloatField(widget=forms.HiddenInput())

    #hidden fields
    food_id = forms.IntegerField(widget=forms.HiddenInput())
    serving_id = forms.IntegerField(widget=forms.HiddenInput())
    units = forms.CharField(widget=forms.HiddenInput())
    quantity = forms.FloatField(widget=forms.HiddenInput())
    metric_quantity = forms.FloatField(widget=forms.HiddenInput())
    metric_units = forms.CharField(widget=forms.HiddenInput())



