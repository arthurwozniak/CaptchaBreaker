'use strict';
////////////////////////////////////////
///  Common variables and functions  ///
////////////////////////////////////////
var archiveEntries;
var allowedFileTypes = ['png', 'jpg', 'jpeg', 'bmp'];
var labels;
var labelsTotal = 0;
var labelsPos = 0;

var operations = ['grayscale', 'treshold', 'filter', 'unmask'];

var step = 1;
var totalSteps = 3;
var stepNextBtn = $('#step-next-btn');

var errors = $('#errors');

var requestFileSystem =
    this.webkitRequestFileSystem ||
    this.mozRequestFileSystem ||
    this.requestFileSystem;
var URL = this.webkitURL || this.mozURL || this.URL;

/* show next step <div> */
function nextStep() {
    hideErrors();
    if (step < totalSteps) {
        $('#step-' + step).hide();
        step++;
        $('#step-' + step).show();
        if (step === totalSteps) {
            $('#step-next').hide();
            fileSelectChanged();
        }
    }
}

/* hide all steps except first after page load */
(function() {
    var i;
    for (i = step + 1; i <= totalSteps; i += 1) {
        $('#step-' + i).hide();
    }
    // disable next step (until enabled in file-select listener)
    stepNextBtn.toggleClass('disabled', true);
    hideErrors();
})();

/* error helpers */

function showErrors(message) {
    errors.show();
    errors.text(message);
}

function hideErrors() {
    errors.hide();
}

/* alert error */
function onerror(message) {
    showErrors(message);
}

////////////////////////////////////////
///  Step-1 variables and functions  ///
////////////////////////////////////////

var fileInput = $('#file-input');
var fileSelect = $('#file-select');

fileSelect.bind('change', fileSelectChanged);

fileInput.bind('change', function() {
    var files;
    console.log('file changed');
    hideErrors();
    files = fileInput.prop('files')[0];
    console.log(files);
    // File selection was aborted
    if (!files) {
        return;
    }

    $('#lbl-' + fileInput.prop('id')).text(files.name);

    // User forced file-chooser to pick-up different file type
    if (files.type !== 'application/zip') {
        showErrors('Only ZIP files are allowed');
        fileInput.val('');
        stepNextBtn.toggleClass('disabled', true);
        return;
    }

    stepNextBtn.toggleClass('disabled', false);

    // read images from archive
    archiveEntries = {};
    model.getEntries(files, function(entries) {
        //fileSelect.innerHTML = "";
        // Filter directories away and process content
        entries
            .filter(function(entry) {
                return !entry.directory;
            })
            .forEach(function(entry) {
                //var option = document.createElement("option");
                //option.text = entry.filename;
                var option = $('<option/>', {
                    text: entry.filename,
                    value: entry.filename,
                });
                option.appendTo(fileSelect);
                console.log(option);
                archiveEntries[entry.filename] = entry;

                //fileSelect.appendChild(option);
            });
    });
});

////////////////////////////////////////
///  Step-2 variables and functions  ///
////////////////////////////////////////

var btnLabelingPrev = $('#btn-labeling-prev');
var btnLabelingNext = $('#btn-labeling-next');

function labelingCancel() {
    console.log('cancel labeling');
    labels = undefined;
    nextStep();
    // workaround for showing first CAPTCHA preview
    fileSelectChanged();
}

function labelingStart() {
    console.log('start labeling');
    stepNextBtn.addClass('disabled');
    labelingValidateButtons();
    $('#step-2-labeling').prop('hidden', false);
    $('#step-2-question').prop('hidden', true);
    $('#text-captcha').prop('disabled', false);
    $('#text-captcha').focus();
    labelsTotal = Object.keys(archiveEntries).length;
    labelsPos = 0;
    labels = {};
    $('#lbl-labeling-total').text(labelsTotal);
    labelingValidateButtons();
    labelingImageForCurrentPos();
}

function labelingValidateButtons() {
    if (labelsPos === 0) {
        // if second parameter is true, class is added, removed otherwised
        btnLabelingPrev.toggleClass('disabled', true);
        return;
    }

    if (labelsPos >= labelsTotal - 1) {
        btnLabelingNext.toggleClass('disabled', true);
        //$("#btn-labeling-done").prop("hidden", false)
        return;
    }
    btnLabelingPrev.toggleClass('disabled', false);
    btnLabelingNext.toggleClass('disabled', false);
}

function labelingImageForCurrentPos() {
    $('#lbl-labeling-current').text(labelsPos + 1);
    // Error, image out of range
    if (!(0 <= labelsPos && labelsPos < labelsTotal)) {
        return;
    }
    model.getBlobFromEntry(Object.values(archiveEntries)[labelsPos], function(
        blob,
    ) {
        console.log(blob);
        var imageUrl = URL.createObjectURL(blob);
        $('#img-captcha-label').attr('src', imageUrl);
    });
}

function labelingImageNext() {
    console.log('next image');
    if (labelsPos >= labelsTotal - 1) {
        console.log("Can't go forward");
        return;
    }
    // cannot skip when input text is empty
    if ($('#text-captcha').val() === '') {
        console.log('empty text');
        $('#text-captcha').focus();
        return;
    }
    labels[Object.keys(archiveEntries)[labelsPos]] = $('#text-captcha').val();
    labelsPos += 1;
    labelingValidateButtons();
    labelingImageForCurrentPos();
    $('#text-captcha').val(labels[Object.keys(archiveEntries)[labelsPos]]);
    $('#text-captcha').focus();
}

function labelingImagePrev() {
    console.log('prev image');

    if (labelsPos === 0) {
        console.log('cant go back...');
        return;
    }
    labelsPos -= 1;
    labelingValidateButtons();
    labelingImageForCurrentPos();
    $('#text-captcha').val(labels[Object.keys(archiveEntries)[labelsPos]]);
    $('#text-captcha').focus();
}

// next image when user press ENTER
$('#text-captcha').keypress(function(e) {
    if (e.which === 13) {
        if (labelsPos === labelsTotal - 1) {
            labels[Object.keys(archiveEntries)[labelsPos]] = $('#text-captcha').val();
            if (
                stepNextBtn.hasClass('disabled') &&
                Object.keys(labels).length === labelsTotal
            ) {
                stepNextBtn.removeClass('disabled');
            }
            return false;
        }
        labelingImageNext();
        return false; //<---- Add this line
    }
});

////////////////////////////////////////
///  Step-3 variables and functions  ///
////////////////////////////////////////

var tmp;
var fileImg = $('#img-original');

// zip file-reader model
var model = (function() {
    return {
        getEntries: function(file, onend) {
            zip.createReader(
                new zip.BlobReader(file),
                function(zipReader) {
                    zipReader.getEntries(onend);
                },
                onerror,
            );
        },
        getEntryFileURL: function(entry, creationMethod, onend, onprogress) {
            var writer;
            var zipFileEntry;

            function getData() {
                entry.getData(
                    writer,
                    function(blob) {
                        var blobURL =
                            creationMethod === 'Blob'
                                ? URL.createObjectURL(blob)
                                : zipFileEntry.toURL();
                        onend(blobURL);
                    },
                    onprogress,
                );
            }

            if (creationMethod === 'Blob') {
                writer = new zip.BlobWriter();
                getData();
            } else {
                createTempFile(function(fileEntry) {
                    zipFileEntry = fileEntry;
                    writer = new zip.FileWriter(zipFileEntry);
                    getData();
                });
            }
        },
        getBlobFromEntry: function(entry, onEndCallback) {
            entry.getData(
                new zip.BlobWriter(),
                onEndCallback,
                function(current, total) {
                    // onprogress callback
                    return;
                },
                function(error) {
                    // onerror callback
                    return;
                },
            );
        },
    };
})();

/* convert blob image to base64 */
function blobToBase64(blob, cb) {
    var reader = new FileReader();
    reader.onload = function() {
        var dataUrl = reader.result;
        var base64 = dataUrl.split(',')[1];
        cb(base64);
    };
    reader.readAsDataURL(blob);
}

function jsonifyOperation(node) {
    var obj;
    console.log(node.getAttribute('data-name'), node.value);
    obj = {};
    obj.class = node.getAttribute('data-class');
    obj.name = node.getAttribute('data-name');
    obj.value = node.value;
    return obj;
}

function jsonifyOperations() {
    var node = document.getElementById('operationListSelected');
    var opsHTML = node.getElementsByTagName('li');
    var opsList = [];
    var ops = {};
    var obj;
    var index;
    console.log(opsHTML);
    for (index = 0; index < opsHTML.length; index++) {
        obj = {};
        opsList.push(obj);
        node = opsHTML[index];
        obj.class = node.getAttribute('data-class');
        var inputs = node.getElementsByTagName('input');
        if (inputs.length === 0) {
            continue;
        }
        obj.args = [];
        var j;
        for (j = 0; j < inputs.length; j++) {
            obj.args.push(jsonifyOperation(inputs[j]));
        }
    }
    return opsList;
}

// Create sortable lists

// reference sortable list with all filters from server
var c = Sortable.create(operationListAvailable, {
    group: {
        pull: 'clone',
        put: false,
        name: 'operations',
    },
    sort: false,
});

// sortable list with filter items
var filterOperations = Sortable.create(operationListSelected, {
    group: {
        pull: false,
        put: true,
        name: 'operations',
    },
    onAdd: function(evt) {
        console.log('onAdd.foo:', [evt.item, evt.from]);
        $('.details', evt.item)[0].hidden = false;
    },
    onSort: function(evt) {
        console.log('onUpdate');
        fileSelectChanged();
    },
    filter: '.js-remove',
    onFilter: function(evt) {
        evt.item.parentNode.removeChild(evt.item);
        fileSelectChanged();
    },
});

function postImage(encoded) {
    console.log(encoded);
    var query = {
        image: encoded,
        operations: jsonifyOperations(),
        count: parseInt($('#characters-count').val(), 10),
    };
    console.log('query: ', query);
    var wrapper = $('#img-previews');
    var original = $('#wrapper-img-original');
    var clone;
    var children = wrapper.children();
    while (children.length > 0) {
        if (children.attr('id') !== original.attr('id')) {
            children.remove();
        }
        children = children.next();
    }
    if (query.operations.length === 0) {
        console.log('No operation selected, skipping post...');
        return;
    }
    $.ajax({
        type: 'POST',
        url: './preview2',
        data: JSON.stringify(query),
        dataType: 'html',
        contentType: 'application/json;charset=UTF-8',
        success: function(result) {
            result = JSON.parse(result);
            var i;
            for (i = 0; i < result.length; i++) {
                clone = original.clone();
                clone.attr('id', '');
                clone.find('span').text(result[i][0]);
                clone
                    .find('img')
                    .attr('src', 'data:image/png;base64,' + result[i][1])
                    .attr('id', '');
                console.log(query.operations[i]);
                wrapper.append(clone);
            }
            for (i in result) {
                console.log(i);
                $('#img-' + i).attr('src', 'data:image/png;base64,' + result[i]);
                $('#wrapper-img-' + i).prop('hidden', false);
            }
        },
    });
}

function submit() {
    var r = new FileReader();
    r.addEventListener(
        'load',
        function() {
            var query = {
                file: r.result.substr(28),
                fileName: fileInput.prop('files')[0].name,
                operations: jsonifyOperations(),
                count: parseInt($('#characters-count').val(), 10),
            };
            if (labels) {
                query.labels = labels;
            }
            console.log('query: ', query);
            $.ajax({
                type: 'POST',
                url: './upload',
                data: JSON.stringify(query),
                dataType: 'html',
                contentType: 'application/json;charset=UTF-8',
                success: function(result) {
                    var parsedResult = JSON.parse(result);
                    if (parsedResult.status === 'error') {
                        showErrors(parsedResult.message);
                    } else {
                        window.location = '../' + parsedResult.id;
                    }
                },
            });
        },
        false,
    );
    r.readAsDataURL(fileInput.prop('files')[0]);
}

function showFilterRange() {
    console.log('Filter checkbox clicked');
    if ($('#checkbox-filter-range').is(':checked')) {
        $('#step-3-filter-range').prop('hidden', false);
    } else {
        $('#step-3-filter-range').prop('hidden', true);
    }
    fileSelectChanged();
}

function filterChangedUpper() {
    console.log('Filter upper bound changed');
    fileSelectChanged();
}

function filterChangedLower() {
    console.log('Filter lower bound changed');
    fileSelectChanged();
}

function charactersCountChanged() {
    console.log('Characters count changed');
    fileSelectChanged();
}

function createTempFile(callback) {
    var tmpFilename = 'tmp.dat';
    requestFileSystem(TEMPORARY, 4 * 1024 * 1024 * 1024, function(filesystem) {
        function create() {
            filesystem.root.getFile(
                tmpFilename,
                {
                    create: true,
                },
                function(zipFile) {
                    callback(zipFile);
                },
            );
        }

        filesystem.root.getFile(
            tmpFilename,
            null,
            function(entry) {
                entry.remove(create, create);
            },
            create,
        );
    });
}

//fileSelect.hidden = true;¨

function fileSelectChanged() {
    console.log(fileSelect.val());
    model.getBlobFromEntry(archiveEntries[fileSelect.val()], function(blob) {
        var imageUrl;
        console.log(blob);
        blobToBase64(blob, postImage);
        tmp = blob;
        imageUrl = URL.createObjectURL(blob);
        fileImg.prop('src', imageUrl);
    });
}
