function classificatorTaskStatus(id, status_elem) {
  $.ajax({
    type: 'GET',
    url: './task_status/' + id,
    data: '',
    dataType: 'html',
    contentType: 'application/json;charset=UTF-8',
    success: function(ajax_result) {
      var result;
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
        case 'RECEIVED':
          status_elem.text('VALIDATING: n-fold validation in progress...');
          break;
        default:
          status_elem.text(trainingStatusMessage(result));
      }
    },
    error: function() {
      status_elem.text('ERROR: No response from server');
    },
  });
}

function trainingStatusMessage(result) {
  var message =
    'TRAINING: ' +
    result.current_iteration +
    '/' +
    result.max_iterations +
    ', loss: ' +
    result.loss;
  return message;
}

function updateStatus() {
  $('.classificator-training').each(function() {
    classificatorTaskStatus($(this).data('id'), $(this).find('.status'));
  });
}

updateStatus();
window.setInterval(updateStatus, 5000);
