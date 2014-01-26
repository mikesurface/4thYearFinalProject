from crispy_forms.bootstrap import FormActions, FieldWithButtons
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div
from whattoeat.forms.custom_crispy_layouts import PlainSubmit
from django import forms


class FoodSearchForm(forms.Form):
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
        helper.layout = Layout(
           FieldWithButtons('search_text',PlainSubmit('search','Search',css_class="btn-success ")),
        )
