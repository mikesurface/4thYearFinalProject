/**
 * Created by michael on 24/12/13.
 *
 * Script for overriding bootstrap CSS to set components to correct size in screen
 */



function adjustSearchElements(page_numbers_to_display) {
//adjust search section
    adjustSearchPanel();

//adjust pagination
    adjustPagination(page_numbers_to_display);

//remove pagination and search margins and padding added by bootstrap
    $('#results').css('padding-top',0);
    $('#results').css('margin-top',0);


//set table width to the width of the page content
    $('.table').width($('#page-content-wrapper').width());
}

function adjustSearchPanel(){
    //adjust size of search panel
    $('#searchpanel').width($('#page-content-wrapper').width());

}

function adjustPagination(page_numbers_to_display){
    //set page button size. +2 term accounts for first/last page buttons
    var pagination = $('.pagination');
    pagination.width($('.wrapper').width);

    $('.pagination_button').each(function(){
       $(this).width($('.pagination').width() / (page_numbers_to_display + 2));
    })

    //remove pagination margins. Note this must be done every time the new results are loaded
    //as a new paginator is built for each page loaded
    pagination.css('margin', 0);
    pagination.css('padding', 0);
}