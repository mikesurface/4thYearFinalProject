from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from whattoeat.accounts.forms import UserRegistrationForm
from whattoeat.utilities import build_user_args


def register(request):
    '''
    Register a new user
    '''
    user_form = UserRegistrationForm()

    if request.method.upper() == 'POST':
        data = request.POST.copy()
        user_form = UserRegistrationForm(data)
        if user_form.is_valid():
            user_form.save(data)

            new_user = auth.authenticate(username=request.POST['username'],
                                    password=request.POST['password1'])
            auth.login(request, new_user)
            return HttpResponseRedirect('/accounts/register_success/')

    return render_to_response('auth_templates/registration.html',
                              {'user_form':user_form},
                              context_instance=RequestContext(request))

@login_required()
def reg_success(request):
    '''
    New user successfully registered
    '''
    args = build_user_args(request)
    return render_to_response('auth_templates/registration_success.html',args)

def login(request):
    '''
    Log in a user
    '''
    login_failed = False

    if request.method.upper() == 'POST':
        username = request.POST.get('username','')
        password = request.POST.get('password','')

        #check details match
        user = auth.authenticate(username=username,password=password)

        #details match and account is still available
        if user is not None and user.is_active:
            auth.login(request,user)
            return HttpResponseRedirect('/')
            #return to home page with user logged in
        else:
            login_failed = True

    #user is not logged in or login failed due to wrong details
    return render_to_response('auth_templates/login.html',{'login_failed':login_failed},context_instance=RequestContext(request))

@login_required
def logout(request):
    '''
    Log the current user out
    '''
    auth.logout(request)
    return HttpResponseRedirect('/accounts/logout_success/')

def logout_success(request):
    '''
    Direct user to a success page after logging out
    '''
    return render_to_response('auth_templates/logout_sucess.html')