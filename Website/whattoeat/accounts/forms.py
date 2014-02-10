from crispy_forms.bootstrap import FormActions
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from whattoeat.models import DietProfile
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Fieldset,Layout, Submit
from whattoeat.solver_backend import UnitConversions


class UserRegistrationForm(UserCreationForm):
    username = forms.CharField(
        max_length=30,
        label = "Username",
        required=True,
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(),
        max_length=30,
        min_length=8,
        label = "Choose a Password",
        required=True,
    )
    password2= forms.CharField(
        widget=forms.PasswordInput(),
        max_length = 30,
        min_length = 8,
        label = "Confirm Password",
        required=True,
    )
    email = forms.EmailField(
        label = "Email",
        required='True',
    )
    first_name = forms.CharField(
        max_length=30,
        label = "First Name",
        required=False,
    )
    last_name = forms.CharField(
        max_length=30,
        label = "Surname",
        required=False,
    )

    class Meta:
        model = User
        fields = ("username","password1","password2","first_name","last_name","email")

    def __init__(self,*args,**kwargs):
        super(UserRegistrationForm,self).__init__(*args,**kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "POST"
        self.helper.form_action = "."
        self.helper.form_id = "user_registration_form"
        self.helper.form_class = 'form-horizontal' #bootstrap horizontal forms
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = "col-lg-6"
        self.helper.layout = Layout(
            Fieldset(
                'Please enter your details:',
                'username',
                'password1',
                'password2',
                'email',
                'first_name',
                'last_name',
            ),

            FormActions(
                Submit('submit','Submit',css_class='btn-primary btn-lg',)
            )
        )



    def save(self, commit=True):
        user = super(UserRegistrationForm,self).save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']

        if commit:
            user.save()

        return user


class DietProfileForm(forms.ModelForm):
    height_units = forms.ChoiceField(
        choices = (('cm','cm'),('inches','inches')),
        required=True,
    )

    weight_units = forms.ChoiceField(
        choices = (('kg','kg'),('lbs','lbs')),
        required = True,
    )

    class Meta:
        model = DietProfile
        fields = ("gender","age","height","weight","goal")

    def __init__(self, *args, **kw):
        super(DietProfileForm, self).__init__(*args, **kw)


    def clean_height_units(self):
        '''
        Convert height to correct value for selected units
        '''
        data = self.cleaned_data
        height = data['height']
        units = data['height_units']
        if units == 'cm':
            data['height'] = height / 100 #convert to m
        elif units == 'inches':
            data['height'] = height * UnitConversions.INCHES_TO_M
        else:
            raise ValidationError("Invalid Height Units")

    def clean_weight_units(self):
        '''
        Convert weight to correct value for selected units
        '''
        data = self.cleaned_data
        weight = data['weight']
        units = data['weight_units']

        if units == 'kg':
            pass #already in correct units
        elif units == 'lbs':
            data['weight'] = weight * UnitConversions.POUNDS_TO_KILOS
        else:
            raise ValidationError("Invalid Weight Units")
