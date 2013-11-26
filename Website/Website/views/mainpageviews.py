from django.http import HttpResponse
from django.shortcuts import render_to_response

def home_page(request):
    return render_to_response("home.html",{})

def login(request):
    html = "<html><head><title>Login</title></head><body>This is the login page (to be implemented)</body></html>"
    return HttpResponse(html)

def register(request):
    html = "<html><head><title>Main Page</title></head><body>This is the registration page (to be implemented)</body></html>"
    return HttpResponse(html)

def mealgenerator_no_user(request):
    html = "<html><head><title>Meal Generator (No User)</title></head><body>This is the meal generator page for non registered users (to be implemented)</body></html>"
    return HttpResponse(html)
