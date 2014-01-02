/**
 * Created by michael on 27/12/13.
 */

/**Ajax method for looking up an ingredient
 On success initialize a dialog containing info on the ingredient
 */

function lookup_ingredient(food_id,food_name){

    $.ajax({
        type: 'GET',
        url: '/search_ingredients/lookup/',
        data: {
            'food_id': food_id,
            'food_name': food_name
        },
        success: create_food_dialog,
        dataType: 'html'
  });
}


function create_food_dialog(data, textStatus, jqXHR){
    $('#ingredient_modal_space').html(data); //render the modal contents in the page


     //make the initial serving visible
    var initial = "#" + $("#serving_selector option:selected").val().toString();

    $(initial).css({'display': 'block'});


    //DEFINE MODAL BEHAVIOUR
    //now open the modal
    var modal = $('#ingredient_modal');
    modal.dialog({
        modal: true,
        buttons: {
            'Close': function () {
                $(this).dialog("close");
            }
        },
        position: {'my':'center','at':'center top','of':'.wrapper'}
    });

    //handle a change to the selection
    $("#serving_selector").change(function () {

        //set all of the servings to be invisible
        $("#serving_selector option").each(function () {
            var id = "#" + $(this).val().toString();
            $(id).css('display', 'none');
        });


        //now make the selected serving visible
        $("#serving_selector option:selected").each(function () {
            var id = "#" + $(this).val().toString();
            $(id).css({'display': 'block', 'width': '100%'});
        });
    });

      //when closed we must completely destroy the dialog
    modal.on("dialogclose",function(){
        initial.css('display','none'); //clear all trace of the dialogue when closed
        $(this).dialog("destroy"); //destory the dialog so it does not affect others
    });



}