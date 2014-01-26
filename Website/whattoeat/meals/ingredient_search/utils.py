import collections
import json
import requests
from requests_oauthlib import OAuth1
from whattoeat.API_Info import API_Codes
from whattoeat.meals.fatsecret_wrappers.foods import Serving, GenericFoodDescription, BrandedFoodDescription

NUMBER_PAGES_TO_DISPLAY = 20
MAX_RESULTS = 50


def pagination_numbers(active_page, number_pages_displayed, total_pages):
    '''
    Calculate the pages to be displayed in the paginator and return this as a list
    '''
    if active_page <= (number_pages_displayed / 2):#page is close to start
        return range(0, number_pages_displayed + 1)
    elif active_page >= (total_pages - (number_pages_displayed / 2)): #page is close to end
        return range(total_pages - number_pages_displayed - 1, total_pages)
    else:
        return range(active_page - (number_pages_displayed / 2), active_page + (number_pages_displayed / 2) + 1)


def fatSecretSearchCall(search_text, page_number, max_results):
    '''
    Make a foods.ingredient_search call to the FatSecret API and return a dictionary representing the JSON ouput of this call.
    The data contains the foods found in the nth page of the ingredient_search results for the input ingredient_search text.
    See FatSecret API foods.ingredient_search for explanation of this format.
    '''
    #set up url for request
    url = API_Codes.FAT_SECRET_URL

    #set upt OAuth1 accounts using FatSecret keys
    auth = OAuth1(API_Codes.FAT_SECRET_API_KEY,
                  API_Codes.FAT_SECRET_API_SECRET,
                  signature_type='query')

    #add params for ingredient_search
    params = {'search_expression': search_text,
              'method': 'foods.search',
              'format': 'json', #json output by default
              'max_results': max_results,
              'page_number': page_number, }

    #make the request
    request = requests.get(url, auth=auth, params=params)

    #parse the returned json
    result = json.loads(request.text)

    return result


def extractResults(search_results):
    '''
    Extracts the foods from an ingredient_search call and returns a list of FoodDescription objects.
    If there are no results, an empty list is returned.
    '''


    #make sure something was returned
    #try:
    #throw away parts we dont need: only need food data
    result = search_results['foods']['food']

    #build the results into an array
    foods = []
    for i in range(0, len(result)):
        try:
            name = result[i]['food_name'],
            id = result[i]['food_id'],
            url = result[i]['food_url'],
            description = result[i]['food_description']

            if result[i]['food_type'] == 'Brand': #deal with branded food types
                foods.append(BrandedFoodDescription(name=name,
                                                    id=id,
                                                    url=url,
                                                    description=description,
                                                    brand=result[i]['brand_name']))
            else:
                foods.append(GenericFoodDescription(name=name,
                                                    id=id,
                                                    description=description,
                                                    url=url))
        except KeyError,TypeError:
            pass #some of the fields missing

    return foods

def extractServing(serving):
    '''
    Takes in a serving entry provided by the food.get method of FatSecretAPI and returns a Serving object
    '''


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

    except (KeyError, TypeError): #problem extracting unavailable info
        return Serving(serving_description, nutrient_vals, None, None, num_units, None)

    #something went completely wrong
    return None


def fatSecretFoodLookupCall(food_id):
    '''
    Returns a list of servings for the food_id.
    Each serving describes the nutritional content for a particular standard quantity than food.
    See FatSecret API foods.get method for more info
    Note that some components returned may be None if information for them is not available from the database.
    '''

    #set up url for request
    url = API_Codes.FAT_SECRET_URL

    #set upt OAuth1 accounts using FatSecret keys
    auth = OAuth1(API_Codes.FAT_SECRET_API_KEY,
                  API_Codes.FAT_SECRET_API_SECRET,
                  signature_type='query')

    #add params for food lookup
    params = {'method': 'food.get',
              'format': 'json',
              'food_id': food_id}

    #make the request
    request = requests.get(url, auth=auth, params=params)


    #parse the returned json
    result = json.loads(request.text)

    servings = []

    result = result['food']['servings']['serving']


    #If there is only one serving, it is returned alone as a single dictionary
    #Otherwise a list of dictionaries is returned
    if isinstance(result, collections.Mapping):
        #add only serving
        servings.append(extractServing(result))
    elif isinstance(result, list):
        for i in range(0, len(result)):
            servings.append(extractServing(result[i]))

    #if result type is neither a list nor dict, empty servings list is returned
    return servings

