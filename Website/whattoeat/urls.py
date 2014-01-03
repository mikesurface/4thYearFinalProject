from django.conf.urls import patterns, include, url

from django.contrib import admin
from whattoeat.views.meal_views.ingredient_search.lookup_ingredient import lookup,lookup_test
from whattoeat.views.meal_views.ingredient_search.search_ingredient import get_results_page
from whattoeat.views.meal_views.ingredient_search.search_ingredient import search_ingredient_base
from whattoeat.views.mainpageviews import *
from whattoeat.views.prototypes import meal_generation_prototype
from whattoeat.views.user_views.registration import register, reg_success
from whattoeat.views.userpageviews import *

admin.autodiscover()

user_urls = patterns('',
    url(r'^diet_profile_edit/$',user_page),                   #edit the diet profile
)

search_urls = patterns('',
    url(r'^update/$', get_results_page),
    url(r'^lookup/$',lookup),
)

urlpatterns = patterns('',
    url(r'^$',home_page),

    url(r'^mealgenerator/', mealgenerator_no_user),     #guides to the meal generator for a user who is not logged in (ie one time usage)
    url(r'^admin/', include(admin.site.urls)),          #admin page

    #registration and log in/out
    url(r'^registration/$',register),
    url(r'^registration_success/$',reg_success),

    #search
    url(r'^search_ingredient/$',search_ingredient_base),
    url(r'^search_ingredient/',include(search_urls)),

    #user pages
    url(r'^user/', include(user_urls)),

    #prototype pages
    url(r'^mealgenerator_prototype/(?P<numIngredients>\d+)/(?P<numRequirements>\d+)/',meal_generation_prototype),
)
