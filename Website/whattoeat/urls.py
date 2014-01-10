from django.conf.urls import patterns, include, url

from django.contrib import admin
from whattoeat.views.meal_views.ingredient_search.lookup_ingredient import lookup
from whattoeat.views.meal_views.ingredient_search.search_ingredient import get_results_page
from whattoeat.views.meal_views.ingredient_search.search_ingredient import search_ingredient_base
from whattoeat.views.mainpageviews import *
from whattoeat.views.prototypes import meal_generation_prototype
from whattoeat.views.user_views.authentication import login, logout, logout_success,register, reg_success
from whattoeat.views.user_views.profile_management import edit_diet_profile, user_homepage
from whattoeat.views.user_views.requirements_management import auto_calculate_requirements_fail, auto_calculate_requirements_success


admin.autodiscover()

requirements_urls = patterns('',
   url(r'^auto_calculate_success/$',auto_calculate_requirements_success),
   url(r'^auto_calculate_fail/$',auto_calculate_requirements_fail),
)

#urls for pages related to altering the users profile and requirements
profile_urls = patterns('',
    url(r'^$',user_homepage),
    url(r'^edit_stats/$',edit_diet_profile),
    url(r'^requirements/',include(requirements_urls)),
)


#urls for user pages
user_urls = patterns('',
    url(r'^login/$',login),
    url(r'^logout/$',logout),
    url(r'^logout_success/$',logout_success),
    url(r'^profile/',include(profile_urls)),
)

search_urls = patterns('',
    url(r'^update/$', get_results_page),
    url(r'^lookup/$',lookup),
)

urlpatterns = patterns('',
    url(r'^$',home_page),

    #admin page
    url(r'^admin/', include(admin.site.urls)),

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
