
$(document).ready(function () {
  var div = $('#more');
  function up() {
    var pk = $('select[name="recipe"]').val();
    div.find('section[id!="recipe-' + pk + '"]:visible').slideUp();
    div.find('#recipe-' + pk + ':hidden').slideDown();
  }
  div.find('section[id!="recipe-' + $('select[name="recipe"]').val() + '"]').hide();
  $('select[name="recipe"]').change(up);
});