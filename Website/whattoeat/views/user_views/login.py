from django.contrib import auth
from django.http.response import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.context import RequestContext

__author__ = 'michael'

def login(request):

    if request.user.is_authenticated():
        return HttpResponseRedirect('') #user already logged in, should never actually be reached

    elif request.method.upper() == 'POST':
        username = request.POST.get('username','')
        password = request.POST.get('password','')

        #check details match
        user = auth.authenticate(username=username,password=password)

        #details match and account is still available
        if user is not None and user.is_active:
            auth.login(request,user)
            return HttpResponseRedirect('')
            #return to home page with user logged in

    #user is not logged in or login failed due to wrong details
    return render_to_response('user_pages/login.html',context_instance=RequestContext())