from django.shortcuts import render_to_response
from whattoeat.utilities import build_user_args


def home_page(request):
    args = build_user_args(request)
    return render_to_response("base/home.html",args)


