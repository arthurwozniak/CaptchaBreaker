function classifierTaskStatus(id, status_elem) {
  var error_msg = 'ERROR: {}';
  $.ajax({
    type: 'GET',
    url: '../status/' + id,
    data: '',
    dataType: 'html',
    contentType: 'application/json;charset=UTF-8',
    success: function(result) {
      var text;
      result = JSON.parse(result);
      switch (result.state) {
        case 'FAILURE':
          status_elem.text('ERROR: ' + result.status);
          break;
        case 'PENDING':
          status_elem.text('PENDING');
          break;
        case 'SUCCESS':
          console.log(status_elem.closest('.classifier-training').remove());
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
  $('.classifier-training').each(function(elem) {
    status = classifierTaskStatus($(this).data('id'), $(this).find('.status'));
  });
}

updateStatus();
window.setInterval(updateStatus, 5000);
