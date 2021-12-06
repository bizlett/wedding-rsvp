// code sourced from stackoverflow - https://stackoverflow.com/questions/26009589/remove-blank-option-tag-from-select-list
$('select option').filter(function () {
    return !this.value || $.trim(this.value).length == 0 || 
    $.trim(this.text).length == 0;})
    .remove();

$(document).ready(function () {
    $('.tooltipped').tooltip();
    $('.delete-guest-modal').modal(
        e.preventDefault()
    );
})