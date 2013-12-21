from dajax.core import Dajax
from django.shortcuts import render_to_response
import requests
import json
import math
from requests_oauthlib import OAuth1
from Website.API_Info import API_Codes
from Website.fatsecret_wrappers.foods import BrandedFoodDescription, GenericFoodDescription
from Website.forms.food_search import FoodSearchForm



NUMBER_PAGES_TO_DISPLAY = 20

'''
Calculate the pages to be displayed in the paginator and return this as a list
'''
def pagination_numbers(active_page, number_pages_displayed, total_pages):
    if active_page <= (number_pages_displayed/2):#page is close to start
        return range(0,number_pages_displayed + 1)
    elif active_page >= (total_pages - (number_pages_displayed/2)) : #page is close to end
        return range(total_pages - number_pages_displayed - 1, total_pages)
    else:
        return range(active_page-(number_pages_displayed/2), active_page + (number_pages_displayed/2) + 1)

'''Make a foods.search call to the FatSecret API and return a dictionary representing the JSON ouput of this call.
   The data contains the foods found in the nth page of the search results for the input search text.
   See FatSecret API foods.search for explanation of this format.
'''
def fatSecretSearchCall(search_text,page_number,max_results):
#set up url for request
    url = API_Codes.FAT_SECRET_URL

    #set upt OAuth1 authentication using FatSecret keys
    auth = OAuth1(API_Codes.FAT_SECRET_API_KEY,
                  API_Codes.FAT_SECRET_API_SECRET,
                  signature_type='query')

    #add params for search
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

'''
Extracts the foods from an search call and returns a list of FoodDescription objects.
If there are no results, an empty list is returned.
'''
def extractResults(search_results):
    #make sure something was returned
    try:
        #throw away parts we dont need: only need food data
        result = search_results['foods']['food']

        #build the results into an array
        foods = []
        for i in range(0, len(result)):
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
    #if any problems in processing data (caused by lack of results or wrong result type)
    except (KeyError, TypeError):
        foods = []

    return foods


'''
Searches for an ingredient in the database and returns the results.
Should only be used for the initial page (page 0) of results, ie when searching for a new food.
AJAX methods handle the retrieval of subsequent pages for the same food.
See ajax.py for update method
'''
def search_ingredient(request, page_number=0, max_results=50):
    #catch input errors to call
    if max_results < 1 :
        max_results = 1

    #validate page number
    page_number = int(page_number)
    if page_number < 0:
        page_number = 0

    #page numbers to be displayed in the pagination bar
    page_numbers_to_display = []

    if request.method.upper() == 'GET':
        search_form = FoodSearchForm(request.GET)
        if search_form.is_valid():
            #retrieve search text
            search_text = search_form.cleaned_data['search_text']

            #call API search
            result = fatSecretSearchCall(search_text, page_number, max_results)

            #get the total results found and the total number of pages
            total_results = int(result['foods']['total_results'])
            total_number_pages = int(math.ceil(total_results / max_results)) + 1

            #extract the food descriptions from the results
            foods = extractResults(result)

            page_numbers_to_display = pagination_numbers(page_number, NUMBER_PAGES_TO_DISPLAY, total_number_pages)
            return render_to_response('meal_pages/ingredient_search/ingredients_search.html',
                                      {'search_results':foods,
                                       'search_text':search_text,
                                       'form':search_form,
                                       'total_results':total_results,
                                       'total_pages':total_number_pages,
                                       'page_number': page_number,
                                       'page_numbers_to_display':page_numbers_to_display,
                                       'last_page':total_number_pages-1,
                                      })
    search_form = FoodSearchForm()
    return render_to_response('meal_pages/ingredient_search/ingredients_search.html',
                              {'form':search_form,
                               })