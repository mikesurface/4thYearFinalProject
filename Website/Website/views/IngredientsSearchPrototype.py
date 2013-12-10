from django.shortcuts import render_to_response
import requests
import json
from requests_oauthlib import OAuth1
from requests_oauthlib.oauth1_session import OAuth1Session
from Website.API_Info import API_Codes
from Website.fatsecret_wrappers.foods import BrandedFoodDescription, GenericFoodDescription
from Website.forms.food_search import FoodSearchForm



def search_ingredient(request,max_results = 50, format = 'json'):
    #should be set to true only if at least one result was found from search
    some_results_found = False

    if request.method.upper() == 'GET':
        search_form = FoodSearchForm(request.GET)
        if search_form.is_valid():
            #retrieve search text
            search_text = search_form.cleaned_data['search_text']

            #set up url for request
            url = API_Codes.FAT_SECRET_URL

            #set upt OAuth1 authentication using FatSecret keys
            auth = OAuth1(API_Codes.FAT_SECRET_API_KEY,
                          API_Codes.FAT_SECRET_API_SECRET,
                          signature_type='query')

            #add params for search
            params = {'search_expression': search_text,
                      'method': 'foods.search',
                      'format': 'json', #json output
                      'max_results': max_results, }

            #make the request
            request = requests.get(url, auth=auth, params=params)

            #parse the returned json
            result = json.loads(request.text)

            #make sure something was returned
            try:
                #throw away parts we dont need: only need food data
                result = result['foods']['food']

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
                some_results_found = True

            except KeyError:
                foods = []

            return render_to_response('meal_pages/ingredients_search.html',
                                      {'search_results':foods,
                                       'form':search_form,
                                       'some_results_found':some_results_found
                                      })
    search_form = FoodSearchForm()
    return render_to_response('meal_pages/ingredients_search.html',
                              {'form':search_form,
                               'results_found':some_results_found})