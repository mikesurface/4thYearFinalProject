from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from whattoeat.models import DietProfile


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)

    class Meta:
        model = User
        fields = ("username","password1","password2","first_name","last_name","email")

    def save(self, commit=True):
        user = super(UserRegistrationForm,self).save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']

        if commit:
            user.save()

        return user


class DietProfileForm(forms.ModelForm):
    class Meta:
        model = DietProfile
        fields = ("gender","age","height","weight","goal")
