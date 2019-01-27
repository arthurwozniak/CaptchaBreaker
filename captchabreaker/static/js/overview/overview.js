function classificatorTaskStatus(id, status_elem) {
  $.ajax({
    type: 'GET',
    url: './task_status/' + id,
    data: '',
    dataType: 'html',
    contentType: 'application/json;charset=UTF-8',
    success: function(ajax_result) {
      var text;
      result = JSON.parse(ajax_result);
      switch (result.state) {
        case 'FAILURE':
          status_elem.text('ERROR: ' + result.status);
          break;
        case 'PENDING':
          status_elem.text('PENDING');
          break;
        case 'SUCCESS':
          status_elem.closest('.classificator-training').remove();
          break;
        default:
          text =
            'TRAINING: ' +
            result.current_iteration +
            '/' +
            result.max_iterations +
            ', loss: ' +
            result.loss;
          status_elem.text(text);
      }
    },
    error: function() {
      status_elem.text('ERROR: No response from server');
    },
  });
}

function updateStatus() {
  $('.classificator-training').each(function(elem) {
    status = classificatorTaskStatus(
      $(this).data('id'),
      $(this).find('.status'),
    );
  });
}

updateStatus();
window.setInterval(updateStatus, 5000);
