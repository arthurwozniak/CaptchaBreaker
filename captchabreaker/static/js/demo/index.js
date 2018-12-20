var fileSelect = $('#file-select');
var fileLabel = $('#file-select-label');
var b64Image = null;
var spinner = $('#spinner');

function imageSelected() {
  console.log(fileSelect.prop('files')[0]['name']);
  $('#img-preview').show();
  $('#file-select-label').show();
  fileLabel.text(fileSelect.prop('files')[0]['name']);
  if (fileSelect.prop('files') && fileSelect.prop('files')[0]) {
    console.log('FOOOO');
    var FR = new FileReader();

    FR.addEventListener('load', function(e) {
      $('#img-preview').attr("src", e.target.result);
      b64Image = e.target.result;
    });

    FR.readAsDataURL(fileSelect.prop('files')[0]);
  }
}

function submit() {
  $('#notification-error').hide();
  $('#notification-success').hide();
  if (b64Image == null) {
    showError('You have to provide all data');
    return;
  }

  spinner.show();
  $.ajax({
    type: 'POST',
    url: './decode',
    data: JSON.stringify({
      image: b64Image.substr(22),
      'dataset-id': $('input[name=classificator]:checked').val(),
    }),
    dataType: 'html',
    contentType: 'application/json;charset=UTF-8',
    success: function(result) {
      result = JSON.parse(result);
      if (result['status'] == 'error') {
        showError(result['message']);
      } else {
        showResult(result['message']);
      }
    },
    error: function(result) {
      showError(
        'An error has occured. Please try later or select different classificator.',
      );
    },
    complete: function(result) {
      spinner.hide();
    },
  });
}

function showError(message) {
  $('#notification-error').text(message);
  $('#notification-error').show();
}

function showResult(message) {
  $('#decoded-text').text(message);
  $('#notification-success').show();
}

(function f() {
  spinner.hide();
  $('#img-preview').hide();
  $('#file-select-label').hide();
  $('#notification-error').hide();
  $('#notification-success').hide();
})();
