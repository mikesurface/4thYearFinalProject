
function registerDeletes(){
     //register delete buttons
    $(".delete_ingredient").click(function () {
        var formid = '.ingredients_space';
        $(this).parents(formid).remove();
        var formCount = parseInt($('#id_ingredients-TOTAL_FORMS').val());
        var forms = $(formid); // Get all the forms
        // Update the total number of forms (1 less than before)
        formCount = forms.length;
        $('#id_ingredients-TOTAL_FORMS').val(formCount);

        for (i = 0; i < formCount; i++) {
                var inputs = $(forms[i]).find('*');
                for(j=0;j<inputs.length;j++){
                    updateElementIndex(inputs[j],'ingredients',i);
            }
        }

    });
}

function add_ingredient(data, textStatus, jqXHR) {
    $('#ingredients_list_table').append(data); //add new ingredient to list

    //update formset data and ingredient indices
    //change total number of formsets
    var forms = $('.ingredients_space');
    var noForms = forms.length;
    $('#id_ingredients-TOTAL_FORMS').val(noForms);

    //map the new forms attributes to a style acceptable by formsets
    //add numbers to form ids to match formset style
    var inputs = $('.ingredients_space:last').find('input');
    for (j = 0; j < inputs.length; j++) {
        var cursor = $(inputs[j]);
        if(cursor.attr('id') == undefined){
            continue;
        }
        var field_name = cursor.attr('id');
        cursor.attr('id', 'id_ingredients-'+(noForms-1)+'-'+ cursor.attr('id').substring(3));
        cursor.attr('name','ingredients-' + (noForms-1) + '-' +cursor.attr('name'));
    }
    //and update the index of each form
    for (i = 0; i < noForms; i++) {
        updateElementIndex(forms[i], 'ingredients', i);
    }

    //register delete button for this new entry
    registerDeletes();



}

function generate_form_handler(form){
    return function() {
        //e.preventDefault();
        var serializedform = form.serialize();
        $.ajax({
                type: form.attr('method'),
                url: '/search_ingredient/serving_to_ingredient/',
                data: serializedform,
                success: function(data, textStatus, jqHXR){
                    add_ingredient(data, textStatus, jqHXR);
                },
                error: function () {
                    alert("Ingredient could not be added");
                }
            }
        );
        $('#ingredient_modal').trigger("dialogclose"); //close serving modal
        $('#ingredients_search_modal').trigger("dialogclose");//close compressed search
        return false;
    }

}

$(document).on("ing_lookup", function () {
    //when an ingredient is looked up, register form behaviour for the different servings
    var serving_forms = $('.serving_data_form');
    for (var i = 0; i < serving_forms.length; i++) {
        var form = $('#serving_data_form_' + i);
        form.submit( generate_form_handler(form) );
    }


});

$(document).ready(function () {
    //make food name visible in forms
    var forms = $('.ingredients_space');
    var noForms = forms.length;
    for(i = 0; i < noForms; i++){
        var form = $(forms[i]);
        var name = $(form.find('#id_ingredients-'+i+'-food_name')).val();
        var desc = $(form.find('#id_ingredients-'+i+'-description')).val();
        var target = $(form.find('.food_name_and_desc'));
        target.html(name+": " + desc);

        registerDeletes();
    }







});


