from django.conf.urls import patterns, include, url

from django.contrib import admin
from Website.views.mainpageviews import *
from Website.views.prototypes import meal_generation_prototype
from Website.views.userpageviews import *

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
    url(r'^(?P<username>\w{6,20})[/]?$', user_page),    #user page
    url(r'^(?P<username>\w{6,20})/', include(userURLs)),
    url(r'^mealgenerator/', mealgenerator_no_user),     #guides to the meal generator for a user who is not logged in (ie one time usage)
    url(r'^admin/', include(admin.site.urls)),          #admin page
    #prototype pages
    url(r'^mealgenerator_prototype/(?P<numIngredients>\d+)/(?P<numRequirements>\d+)/',meal_generation_prototype)
)