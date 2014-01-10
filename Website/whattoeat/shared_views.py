from django.http.response import HttpResponseRedirect
from django.shortcuts import render

# Create your views here.


'''
Checks if a user is logged in. If not they are redirected to the login page and
if they login successfully will return to where they were
'''
def check_user_logged_in(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/user/login/?next=%s' % request.path)