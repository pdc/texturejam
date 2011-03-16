
$(document).ready(function () {
  var progress = $('#progress');
  var progressUrl = progress.attr('data-href');
  var ol = $('<ol>').appendTo(progress);
  var up = function () {
    $.ajax(progressUrl, {
      dataType: 'json',
      success: function (data, textStatus, jqXHR) {
        for (var i = 0; i < data.steps.length; ++i) {
          var step = data.steps[i];
          var li = $('#' + step.name);
          if (step.percent == 100) {
            li.removeClass('incomplete').addClass('complete');
          } else {
            li.removeClass('complete').addClass('incomplete');
          }
        }

        if (data.isComplete) {
          progress.find('p').addClass('complete');
          var p = $('<p>').addClass('next').text('Finished! Now go to ').appendTo(progress);
          $('<a>').attr('href', data.href).text(data.label).appendTo(p);
        } else if (data.milliseconds) {
          window.setTimeout(up, data.milliseconds);
        }
      }
    });
  };
  up();
});