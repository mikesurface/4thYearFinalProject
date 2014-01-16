from django.contrib import auth
from django.http.response import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from whattoeat.forms.user_forms import  UserRegistrationForm

def register(request):
    user_form = UserRegistrationForm()

    if request.method.upper() == 'POST':
        data = request.POST.copy()
        user_form = UserRegistrationForm(data)
        if user_form.is_valid():
            new_user = user_form.save(data)

            new_user = auth.authenticate(username=request.POST['username'],
                                    password=request.POST['password1'])
            auth.login(request, new_user)
            return HttpResponseRedirect('/registration_success/')

    return render_to_response('user_pages/authentication/registration.html',
                              {'user_form':user_form},
                              context_instance=RequestContext(request))

def reg_success(request):
    return render_to_response('user_pages/authentication/registration_success.html',{'user':request.user})

def login(request):
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
    return render_to_response('user_pages/authentication/login.html',{'login_failed':login_failed},context_instance=RequestContext(request))

def logout(request):
    auth.logout(request)
    return HttpResponseRedirect('/user/logout_success/')

def logout_success(request):
    return render_to_response('user_pages/authentication/logout_sucess.html')