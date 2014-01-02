from django.conf.urls import patterns, include, url

from django.contrib import admin
from whattoeat.views.meal_views.ingredient_search.lookup_ingredient import lookup,lookup_test
from whattoeat.views.meal_views.ingredient_search.search_ingredient import get_results_page
from whattoeat.views.meal_views.ingredient_search.search_ingredient import search_ingredient_base
from whattoeat.views.mainpageviews import *
from whattoeat.views.prototypes import meal_generation_prototype
from whattoeat.views.userpageviews import *

admin.autodiscover()

userURLs = patterns('',
    #url(r'^\$',user_page),                                   #users homepage
    url(r'^saved_meals/',saved_meals),                        #overview of saved meals
    url(r'^saved_meal/(?P<meal_id>\w+)/',retrieve_saved_meal),#retrieves a specific saved meal
    url(r'^personal_info/',personal_info),                    #user can see/alter their personal info
    url(r'mealgenerator/',mealgenerator),                     #brings up mealgenerator for logged in user
)

urlpatterns = patterns('',
    url(r'^$',home_page),
    url(r'^login/', login),                             #login
    url(r'^register/' ,register),                       #register

    url(r'^mealgenerator/', mealgenerator_no_user),     #guides to the meal generator for a user who is not logged in (ie one time usage)
    url(r'^admin/', include(admin.site.urls)),          #admin page

    #prototype pages
    url(r'^mealgenerator_prototype/(?P<numIngredients>\d+)/(?P<numRequirements>\d+)/',meal_generation_prototype),
    
    url(r'^lookup_test/(?P<food_id>\d+)',lookup_test),
    url(r'^search_ingredients/update/$', get_results_page),
    url(r'^search_ingredients/lookup/$',lookup),
    url(r'^search_ingredients/',search_ingredient_base),
   

    url(r'^(?P<username>\w{6,20})[/]?$', user_page),    #user page
    url(r'^(?P<username>\w{6,20})/', include(userURLs)),
)
