import math
from django.shortcuts import render_to_response
from whattoeat.meals.ingredient_search.forms import FoodSearchForm
from whattoeat.meals.ingredient_search.utils import MAX_RESULTS, fatSecretSearchCall, extractResults, NUMBER_PAGES_TO_DISPLAY, pagination_numbers
from whattoeat.utilities import build_user_args


def search_ingredient_base(request, max_results=MAX_RESULTS):
    '''
    Searches for an ingredient in the database and returns the results.
    Should only be used for the initial page (page 0) of results, ie when searching for a new food.
    AJAX methods handle the retrieval of subsequent pages for the same food.
    '''
    args = build_user_args(request)
    #catch input errors to call
    if max_results < 1:
        max_results = 1

    if request.method.upper() == 'GET':
        page_number = 0

        #page numbers to be displayed in the pagination bar
        page_numbers_to_display = []

        search_form = FoodSearchForm(request.GET)
        if search_form.is_valid():
            #retrieve ingredient_search text
            search_text = search_form.cleaned_data['search_text']

            #call API ingredient_search
            result = fatSecretSearchCall(search_text, page_number, max_results)

            try:
                #get the total results found and the total number of pages
                total_results = int(result['foods']['total_results'])
                total_number_pages = int(math.ceil(total_results / max_results)) + 1

                #extract the food descriptions from the results
                foods = extractResults(result)

                #calculate page numbers to be displayed in the paginator
                page_numbers_to_display = pagination_numbers(page_number, NUMBER_PAGES_TO_DISPLAY, total_number_pages)

            #catch problems with API
            except (KeyError, TypeError):
                total_results = 0
                total_number_pages = 0
                page_numbers_to_display = 0
                foods = []

            #process arguments

            args['search_results'] = foods
            args['search_text'] = search_text
            args['form'] = search_form
            args['total_results'] = total_results
            args['total_pages'] = total_number_pages
            args['page_number'] = page_number
            args['page_numbers_to_display'] = page_numbers_to_display
            args['last_page'] = total_number_pages - 1

            return render_to_response('meal_pages/ingredient_search/ingredients_search_base.html', args)


    #search not yet made or form is invalid
    search_form = FoodSearchForm()
    args['form'] = search_form
    args['not_searched_yet'] = True
    return render_to_response('meal_pages/ingredient_search/ingredients_search_base.html', args)

