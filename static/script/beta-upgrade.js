
$.domReady(function () {
  var prevID = null;
  var heights = {};
  function up() {
    var animationMilliseconds = !prevID ? 0 : 333;
    var recipeID = -1;
    $('select[name="recipe"] option').each(function (el) {
      if (el.selected) {
        recipeID = el.value;
      }
    });
    var sectionID = 'recipe-' + recipeID;
    if (sectionID != prevID) {
      $('#more section').each(function (el) {
        if (!prevID) {
          heights[el.id] = $(el).css('height')
        }
        if (el.id == sectionID) {
          $(el).animate({height: heights[el.id], duration: animationMilliseconds});
        } else if (!prevID || el.id == prevID) {
          $(el).animate({height: 0, overflow: 'hidden', duration: animationMilliseconds})
        }
      });
      prevID = sectionID;
    }
  }
  up(0);
  $('select[name="recipe"]').bind('change', up);
});