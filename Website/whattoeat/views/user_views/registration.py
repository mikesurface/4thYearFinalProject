from django.contrib.auth.forms import UserCreationForm
from django.http.response import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from whattoeat.forms.user_forms import DietProfileForm, UserRegistrationForm


def register(request):
    user_form = UserRegistrationForm()

    if request.method.upper() == 'POST':
        data = request.POST.copy()
        user_form = UserRegistrationForm(data)
        if user_form.is_valid():
            new_user = user_form.save(data)
            return HttpResponseRedirect('/registration_success/')

    return render_to_response('user_pages/registration.html',
                              {'user_form':user_form},
                              context_instance=RequestContext(request))

def reg_success(request):
    return render_to_response('user_pages/registration_success.html')