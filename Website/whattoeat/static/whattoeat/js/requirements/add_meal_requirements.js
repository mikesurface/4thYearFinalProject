/**
 * Created by michael on 17/01/14.
 */

function add_meal_requirements_set(){
    $.ajax({
            type: 'POST',
            url: '/user/profile/requirements/add_meal_requirements_set/',
            dataType: 'html',
            success: add_meal_requirements_panel
    });
}

function add_meal_requirements_panel(data, textStatus, jqXHR){
    $('#meal_requirements_set_space').append(data);
}

$('#add_meal_requirements_set_form').submit(function(){
        add_meal_requirements_set()
    }
);