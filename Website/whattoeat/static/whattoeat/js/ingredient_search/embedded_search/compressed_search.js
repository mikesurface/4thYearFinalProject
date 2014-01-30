/**
 * Created by michael on 27/01/14.
 *
 * Note this depends on the loadPage script, and must be loaded first
 * Also depends on base.js, as it uses dynamically height adjusted elements
 */

function display_compressed_search(){
    var modal = $('#ingredients_search_modal');
    modal.dialog({
        modal: true,
        title:'Search for an ingredient',
        width:'95%',
        buttons: {
            'Close': function () {
                $(this).dialog("close");
                modal.css('display','none');
            }
        },
        position: {'my':'center','at':'center top','of':'.wrapper'}
    });

    modal.on("dialogclose",function(){
        $(this).dialog("close");
        modal.css('display','none');

    });

    modal.css({'display':'block','max-height':max_element_height(),'y-overflow':'scroll'});
}


$(document).ready(function(){
        $('#ingredient_search_submit').click(function(){
            var search_text = $('#id_search_text').val();
            loadPage_compressed(search_text,0);
        });
    }
);

