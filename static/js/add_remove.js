// Original author: rmed

const ID_RE = /(-)_(-)/;

function replaceTemplateIndex(value, index) {
    return value.replace(ID_RE, '$1'+index+'$2');
}

function adjustIndices(removedIndex) {
    var $forms = $('.subform');

    $forms.each(function(i) {
        var $form = $(this);
        var index = parseInt($form.data('index'));
        var newIndex = index - 1;

        if (index < removedIndex) {
            return true;
        }

        var regex = new RegExp('(-)'+index+'(-)');
        var repVal = '$1'+newIndex+'$2';

        $form.attr('id', $form.attr('id').replace(index, newIndex));
        $form.data('index', newIndex);

        $form.find('label, input, select, textarea').each(function(j) {
            var $item = $(this);

            if ($item.is('label')) {
                $item.attr('for', $item.attr('for').replace(regex, repVal));
                return;
            }

            $item.attr('id', $item.attr('id').replace(regex, repVal));
            $item.attr('name', $item.attr('name').replace(regex, repVal));
        });
    });
}

function removeForm() {
    var $removedForm = $(this).closest('.subform');
    var removedIndex = parseInt($removedForm.data('index'));

    $removedForm.remove();

    adjustIndices(removedIndex);
}

function addForm() {
    var $templateForm = $('#lap-_-form');

    if ($templateForm.length === 0) {
        console.log('[ERROR] Cannot find template');
        return;
    }

    var $lastForm = $('.subform').last();

    var newIndex = 0;

    if ($lastForm.length > 0) {
        newIndex = parseInt($lastForm.data('index')) + 1;
    }

    if (newIndex >= 20) {
        console.log('[WARNING] Reached maximum number of elements');
        return;
    }

    var $newForm = $templateForm.clone();

    $newForm.attr('id', replaceTemplateIndex($newForm.attr('id'), newIndex));
    $newForm.data('index', newIndex);

    $newForm.find('label, input, select, textarea').each(function(idx) {
        var $item = $(this);

        if ($item.is('label')) {
            $item.attr('for', replaceTemplateIndex($item.attr('for'), newIndex));
            return;
        }

        $item.attr('id', replaceTemplateIndex($item.attr('id'), newIndex));
        $item.attr('name', replaceTemplateIndex($item.attr('name'), newIndex));
    });

    $('#subforms-container').append($newForm);
    $newForm.addClass('subform');
    $newForm.removeClass('is-hidden');

    $newForm.find('.remove').click(removeForm);
}


$(document).ready(function() {
    $('#add').click(addForm);
    $('.remove').click(removeForm);
});