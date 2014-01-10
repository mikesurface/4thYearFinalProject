/**
 * Created by michael on 22/12/13.
 */

/**Loads a page of search results for the given search text using an AJAX request*/
function loadPage(search_text, page_number) {
    $.ajax({
        type: 'GET',
        url: '/search_ingredient/update/',
        data: {
            'search_text': search_text,
            'page_number': page_number
        },
        success: loadSuccess,
        dataType: 'html'
    });
}

/**Changes the results sections to render the new page*/
function loadSuccess(data, textStatus, jqXHR) {
    $('#ingredient_search_results').html(data);
}
