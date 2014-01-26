import math

__author__ = 'michael'

from django.shortcuts import render_to_response
from django.http.response import HttpResponseBadRequest
from whattoeat.meals.ingredient_search.utils import fatSecretFoodLookupCall, fatSecretSearchCall, extractResults, NUMBER_PAGES_TO_DISPLAY, pagination_numbers

__author__ = 'michael'





def lookup(request):
    '''
    AJAX compatible method for looking up an ingredient in the database.
    Request takes a food_id (the unique identifier for the food) and the food_name and returns a list of servings.
    '''

    if request.method.upper() == 'GET': #only form of method which should be used
        food_id = int(request.GET['food_id'])
        food_name = str(request.GET['food_name'])

        servings = fatSecretFoodLookupCall(food_id)
        return render_to_response('meal_pages/ingredient_search/modal/ingredient_lookup_modal.html',
                                  {
                                      'servings': servings,
                                      'food_name': food_name,
                                  })

    else: #for some reason request was not valid
        return HttpResponseBadRequest()





def lookup_test(request, food_id):
    '''
    Test method for ingredient lookup
    '''
    food_id = int(food_id)
    servings = fatSecretFoodLookupCall(food_id)
    return render_to_response('meal_pages/ingredient_search/modal/ingredient_lookup_modal.html', {'servings': servings})

def get_results_page(request, max_results=50):
    '''
    Method used to update the ingredient_search results with AJAX requests
    '''
    #catch input errors to call
    if max_results < 1:
        max_results = 1

    if request.method.upper() == 'GET':
    #retrieve ingredient_search text
        search_text = request.GET['search_text']
        page_number = int(request.GET['page_number'])

        #call API ingredient_search
        result = fatSecretSearchCall(search_text, page_number, max_results)

        try:
            #get the total results found and the total number of pages
            total_results = int(result['foods']['total_results'])
            total_number_pages = int(math.ceil(total_results / max_results)) + 1

            #extract the food descriptions from the results
            foods = extractResults(result)

            #calculate pages to be displayed
            page_numbers_to_display = pagination_numbers(page_number, NUMBER_PAGES_TO_DISPLAY, total_number_pages)

        #catch problems with API
        except (KeyError, TypeError):
            total_results = 0
            total_number_pages = 0
            page_numbers_to_display = 0
            foods = []

        return render_to_response('meal_pages/ingredient_search/results/ingredient_search_results.html',
                                  {'search_text': search_text,
                                   'search_results': foods,
                                   'total_results': total_results,
                                   'total_pages': total_number_pages,
                                   'page_number': page_number,
                                   'page_numbers_to_display': page_numbers_to_display,
                                   'last_page': total_number_pages - 1,
                                  })
    else: #should never happen problem with request
        return HttpResponseBadRequest()

