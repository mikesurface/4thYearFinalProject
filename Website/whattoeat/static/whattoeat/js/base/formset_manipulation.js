/**
 * Created by michael on 28/01/14.
 */

/**
 * Created by michael on 15/01/14.
 * Adapted from http://stellarchariot.com/blog/2011/02/dynamically-add-form-to-formset-using-javascript-and-django/
 */


    // Code adapted from http://djangosnippets.org/snippets/1389/
function updateElementIndex(el, prefix, ndx) {
    var id_regex = new RegExp('(' + prefix + '-\\d+-)');
    var replacement = prefix + '-' + ndx + '-';
    if ($(el).attr("for")) $(el).attr("for", $(el).attr("for").replace(id_regex,
        replacement));
    if (el.id) el.id = el.id.replace(id_regex, replacement);
    if (el.name) el.name = el.name.replace(id_regex, replacement);
}

function deleteForm(btn, prefix) {
    var form_id = "." + prefix + "_space";
    var formCount = parseInt($('#id_' + prefix + '-TOTAL_FORMS').val());
    if (formCount > 1) {
        // Delete the item/form
        $(btn).parents(form_id).remove();
        var forms = $(form_id); // Get all the forms
        // Update the total number of forms (1 less than before)
        formCount = forms.length;
        $('#id_' + prefix + '-TOTAL_FORMS').val(formCount);

        // Go through the forms and set their indices, names and IDs
        for (i = 0; i < formCount; i++) {
            $(forms.get(i)).children().children().each(
                updateElementIndex(this, prefix, i)
            );
        }
    }
    return false;
}
