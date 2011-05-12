
$.domReady(function () {
  function up() {
    var recipeID = -1;
    $('select[name="recipe"] option').each(function (el) {
      if (el.selected) {
        recipeID = el.value;
      }
    });
    var sectionID = 'recipe-' + recipeID;
    $('#more section').each(function (el) {
        el.className = (el.id == sectionID ? 'shown' : 'hidden');
    });
  }
  up();
  $('select[name="recipe"]').bind('change', up);
});