import collections
from django.shortcuts import render_to_response
from django.template.context import RequestContext
import requests, json
from django.http.response import HttpResponseBadRequest
from requests_oauthlib.oauth1_auth import OAuth1
from whattoeat.API_Info import API_Codes
from whattoeat.fatsecret_wrappers.foods import Serving

__author__ = 'michael'

'''
Takes in a serving entry provided by the food.get method of FatSecretAPI and returns a Serving object
'''
def extractServing(serving):
        serving_description = serving['serving_description'] #full description of the serving (e.g. 1 cup)
        num_units = float(serving['number_of_units']) #quantitative component of the above (1 in '1 cup')
        measurement_description = serving['measurement_description'] #unit component ('cup' in '1 cup')

        quantity = 0
        unit = ''

        #process nutrients
        nutrient_vals = {}
        #core (always available)
        nutrient_vals['calories'] = float(serving['calories'])
        nutrient_vals['protein'] = float(serving['protein'])
        nutrient_vals['carbohydrate'] = float(serving['carbohydrate'])
        nutrient_vals['fat'] = float(serving['fat'])
        try:
            #sometimes available
            if 'fiber' in serving: nutrient_vals['fibre'] = float(serving['fiber'])
            if 'sodium' in serving:
                nutrient_vals['salt'] = float(serving['sodium']) * 2.5
            if 'sugar' in serving: nutrient_vals['sugar'] = serving['sugar']
            if 'saturated_fat' in serving: nutrient_vals['satfat'] = serving['saturated_fat']

            #The following are not always available.
            #quanity and unit combine to give a standardised equivalent of the serving measurement
            #i.e. a measurement in grams, ounces or milliletres
            if 'quantity' in serving: quantity = float(serving['metric_serving_amount']) #amount of ingredient.
            if 'metric_serving_unit' in serving: unit = serving['metric_serving_unit'] #unit of measurement (g,oz,etc)

            return Serving(serving_description, nutrient_vals, quantity, unit, num_units, measurement_description)

        except (KeyError,TypeError): #problem extracting unavailable info
            return Serving(serving_description,nutrient_vals,None,None,num_units,None)

        #something went completely wrong
        return None

'''Returns a list of servings for the food_id.
Each serving describes the nutritional content for a particular standard quantity than food.
See FatSecret API foods.get method for more info
Note that some components returned may be None if information for them is not available from the database.
'''
def fatSecretFoodLookupCall(food_id):
    #set up url for request
    url = API_Codes.FAT_SECRET_URL

    #set upt OAuth1 authentication using FatSecret keys
    auth = OAuth1(API_Codes.FAT_SECRET_API_KEY,
                  API_Codes.FAT_SECRET_API_SECRET,
                  signature_type='query')

    #add params for food lookup
    params = {'method': 'food.get',
              'format': 'json',
              'food_id': food_id }

    #make the request
    request = requests.get(url, auth=auth, params=params)


    #parse the returned json
    result = json.loads(request.text)

    servings = []

    result = result['food']['servings']['serving']

    '''
    If there is only one serving, it is returned alone as a single dictionary
    Otherwise a list of dictionaries is returned
    '''
    if isinstance(result, collections.Mapping):
        #add only serving
        servings.append(extractServing(result))
    elif isinstance(result, list):
        for i in range(0, len(result)):
            servings.append(extractServing(result[i]))

    #if result type is neither a list nor dict, empty servings list is returned
    return servings


'''
AJAX compatible method for looking up an ingredient in the database.
Request takes a food_id (the unique identifier for the food) and the food_name and returns a list of servings.
'''
def lookup(request):
    if request.method.upper() == 'GET': #only form of method which should be used
        food_id = int(request.GET['food_id'])
        food_name = str(request.GET['food_name'])

        servings = fatSecretFoodLookupCall(food_id)
        return render_to_response('meal_pages/ingredient_search/modal/ingredient_lookup_modal.html',
            {
                'servings':servings,
                'food_name':food_name,
            })

    else: #for some reason request was not valid
        return HttpResponseBadRequest()


'''
Test method for ingredient lookup
'''
def lookup_test(request,food_id):
    food_id = int(food_id)
    servings = fatSecretFoodLookupCall(food_id)
    return render_to_response('meal_pages/ingredient_search/modal/ingredient_lookup_modal.html',{'servings':servings})