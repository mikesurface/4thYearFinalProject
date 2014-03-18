/**
 * Created by michael on 31/12/13.
 * Script used to fix heights of pages dynamically to fit the browser window
 */

function fixPageHeights() {
    $('.wrapper').height($(window).height() - ($('.banner').height() + $('.sub_banner').height() + 2 * $('.footer').height() + 10));
}

function max_element_height(){
    ///return the max height any element can take while respecting the layout
    return ($(window).height() - ($('.banner').height() + $('.sub_banner').height() + 2 * $('.footer').height() + 10));
}
function adjust(){
    fixPageHeights();
}
$(window).ready(adjust());
$(window).resize(function(){
    adjust();
});
