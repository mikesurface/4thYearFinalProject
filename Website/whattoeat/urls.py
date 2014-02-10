from django.conf.urls import patterns, include, url

from django.contrib import admin
from whattoeat.accounts.auth_views import *
from whattoeat.accounts.user_views import user_homepage, edit_diet_profile
from whattoeat.base_views import home_page
from whattoeat.meals.generation.ajax_methods import serving_to_ingredient_form
from whattoeat.meals.generation.views import meal_generation
from whattoeat.meals.ingredient_search.ajax_methods import lookup, get_results_page
from whattoeat.meals.ingredient_search.views import search_ingredient_base
from whattoeat.requirements_management.daily_requirements_views import *
from whattoeat.requirements_management.meal_requirements_views import*
from whattoeat.requirements_management.views import update_requirements_success, recalculate_base_meal_set

admin.autodiscover()

requirements_urls = patterns('',
   url(r'^auto_calculate/$',calculate_daily_requirements),
   url(r'^auto_calculate_success/$',auto_calculate_requirements_success),
   url(r'^auto_calculate_fail/$',auto_calculate_requirements_fail),
   url(r'^auto_calculate_base_meal_requirements/$',recalculate_base_meal_set),

   url(r'^edit_daily_requirements/$',edit_daily_requirements),
   url(r'^my_daily_requirements/$',view_daily_requirements),

   url(r'^my_meal_requirements/$',view_meal_requirements),
   url(r'^add_meal_requirements/$',add_meal_requirements),
   url(r'^edit_meal_requirements/(?P<name>[\w ]{1,100})/$',edit_meal_requirements),
   url(r'^remove_meal_requirements/(?P<name>[\w ]{1,100})/$',remove_meal_set),

   url(r'^update_requirements_success/$',update_requirements_success)
)



#urls for user pages
user_urls = patterns('',
                     url(r'^$', user_homepage),
                     url(r'^edit_stats/$', edit_diet_profile),
                     url(r'^requirements/',include(requirements_urls)),
)

search_urls = patterns('',
                       url(r'^update/$', get_results_page),
                       url(r'^lookup/$', lookup),
                       url(r'^serving_to_ingredient/$',serving_to_ingredient_form)
)

authentication_urls = patterns('',
                               url(r'login/$', login),
                               url(r'logout/$', logout),
                               url(r'register/$', register),
                               url(r'register_success/$', reg_success),
                               url(r'logout_success/$', logout_success),
)

urlpatterns = patterns('',
                       url(r'^$', home_page),

                       #admin page
                       url(r'^admin/', include(admin.site.urls)),

                       #standard accounts managemment
                       url(r'^accounts/', include(authentication_urls)),

                       #search
                       url(r'^search_ingredient/$', search_ingredient_base),
                       url(r'^search_ingredient/', include(search_urls)),


                       #generation
                       url(r'^meal_generator/$',meal_generation),

                       #user pages
                       url(r'^user/', include(user_urls)),

)
