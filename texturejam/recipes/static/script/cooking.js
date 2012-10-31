/*
* On the ‘remix cooking’ page,
* periodically check for progress
* and update the spinner icons.
*/

$.domReady(function () {
  var progress = $('#progress');
  if (progress) {
    var progressUrl = progress.attr('data-href');

    var updateProgress = function () {
      $.ajax({
        url: progressUrl,
        type: 'json',
        success: function (data) {
          for (var i = 0; i < data.steps.length; ++i) {
            var step = data.steps[i];
            var li = $('#' + step.name);
            if (step.percent == 100) {
              li.removeClass('incomplete').addClass('complete');
            } else if (step.percent > 0) {
              li.addClass('incomplete');
            }
          }

          if (data.isComplete) {
            progress.find('p').addClass('complete');
            progress.find('*')
              .animate({
                height: 0,
                overflow: 'hidden',
                duration: 1000})
            var p = $('<p>').addClass('next').text('Finished! Now go to ').appendTo(progress);
            $('<a>').attr('href', data.href).text(data.label).appendTo(p);
          } else if (data.milliseconds) {
            window.setTimeout(updateProgress, data.milliseconds);
          }
        }
      });
    };
    updateProgress();
  }
});