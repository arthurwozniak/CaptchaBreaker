var archiveEntries;
var allowedFileTypes = ["png", "jpg", "jpeg", "bmp"]
var labels;
var labelsTotal = 0;
var labelsPos = 0;

var operations = ["grayscale", "treshold", "filter", "unmask"]

var step = 1;
var currentBlob;

//$("#wrapper-labeling").hide();
//$("#wrapper-labeling-input").hide();
//$("#wrapper-filter-range").hide()
//$("#file-select").hide();


var requestFileSystem = this.webkitRequestFileSystem || this.mozRequestFileSystem || this.requestFileSystem;
var URL = this.webkitURL || this.mozURL || this.URL;


function onerror(message) {
    alert(message);
}

function blobToBase64(blob, cb) {
    var reader = new FileReader();
    reader.onload = function() {
        var dataUrl = reader.result;
        var base64 = dataUrl.split(',')[1];
        cb(base64);
    };
    reader.readAsDataURL(blob);

};


// given sequence of operations, lets create query for generating images since
// chosen one
function prepareQuery(initOperation) {
    data = {};
    for (var i = Math.max(0, operations.indexOf(initOperation)); i < operations.length; i++) {
        data[operations[i]] = {};
    }
    // TODO: fix logic if we are behind this operation
    if (! $("#checkbox-filter-range").is(":checked")){
        delete data["filter"];
    } else {
        delete data["treshold"];
        data["filter"]["lower"] = parseInt($("#filter-range-lower").val(), 10);
        data["filter"]["upper"] = parseInt($("#filter-range-upper").val(), 10);
    }
    data["unmask"]["count"] = parseInt($("#characters-count").val(), 10);
    tmp = data;
    console.log(data);
    return data;
}

function postImage(encoded) {
    console.log(encoded);
    var query = {
        image: encoded,
        operations: prepareQuery()
    };
    console.log("query: ", query);
    $.ajax({
        type: "POST",
        url: "/foo",
        data: JSON.stringify(query),
        dataType: 'html',
        contentType: 'application/json;charset=UTF-8',
        success: function (result){
            result = JSON.parse(result);
            for (var i in operations){
                console.log("hiding: " + "#wrapper-img-"+i)
                $("#wrapper-img-"+operations[i]).prop("hidden", true);
            }
            for (var i in result){
                console.log(i);
                $("#img-"+i).attr("src", "data:image/png;base64,"+result[i])
                $("#wrapper-img-"+i).prop("hidden", false);
            }
        }
    });
}


function showFilterRange() {
    console.log("Filter checkbox clicked")
    if ($("#checkbox-filter-range").is(":checked")){
        $("#step-3-filter-range").prop("hidden", false);

    }
    else {
        $("#step-3-filter-range").prop("hidden", true);
    }
    fileSelectChanged();
}


function filterChangedUpper() {
    console.log("Filter upper bound changed");
    fileSelectChanged();
}

function filterChangedLower() {
    console.log("Filter lower bound changed");
    fileSelectChanged();
}

function charactersCountChanged() {
    console.log("Characters count changed");
    fileSelectChanged();
}

function createTempFile(callback) {
    var tmpFilename = "tmp.dat";
    requestFileSystem(TEMPORARY, 4 * 1024 * 1024 * 1024, function(filesystem) {
        function create() {
            filesystem.root.getFile(tmpFilename, {
                create: true
            }, function(zipFile) {
                callback(zipFile);
            });
        }

        filesystem.root.getFile(tmpFilename, null, function(entry) {
            entry.remove(create, create);
        }, create);
    });
}

var model = (function() {

    return {
        getEntries: function(file, onend) {
            zip.createReader(new zip.BlobReader(file), function(zipReader) {
                zipReader.getEntries(onend);
            }, onerror);
        },
        getEntryFileURL: function(entry, creationMethod, onend, onprogress) {
            var writer, zipFileEntry;

            function getData() {
                entry.getData(writer, function(blob) {
                    var blobURL = creationMethod == "Blob" ? URL.createObjectURL(blob) : zipFileEntry.toURL();
                    onend(blobURL);
                }, onprogress);
            }

            if (creationMethod == "Blob") {
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


            entry.getData(new zip.BlobWriter(),
                onEndCallback,
                function(current, total) {
                    // onprogress callback
                },
                function(error) {
                    // onerror callback
                });

        }
    };
})();

var tmp;

var fileInput = $('#file-input');
var fileSelect = $('#file-select');
var fileImg = $('#img-original');

var btnLabelingPrev = $('#btn-labeling-prev');
var btnLabelingNext = $('#btn-labeling-next');


//fileSelect.hidden = true;¨

function fileSelectChanged() {
    console.log(fileSelect.val());
    model.getBlobFromEntry(archiveEntries[fileSelect.val()],
        function(blob) {
            console.log(blob);
            blobToBase64(blob, postImage);
            tmp = blob;
            var imageUrl = URL.createObjectURL(blob);
            fileImg.prop("src", imageUrl);
        });
}

fileSelect.bind('change', fileSelectChanged);

fileInput.bind('change', function() {
    console.log("file changed")
    var files = fileInput.prop('files')[0];
    console.log(files);
    // File selection was aborted
    if (!files) {
        return;
    }
    // User forced file-chooser to pick-up different file type
    if (files.type !== "application/zip") {
        alert("Only ZIP files are allowed");
        fileInput.val("")
        return;
    }

    // show selected file and disable btn
    $("#lbl-"+fileInput.prop("id")).text(fileInput.val());
    $("#btn-"+fileInput.prop("id")).toggleClass( "btn-primary", false );
    $("#btn-"+fileInput.prop("id")).toggleClass( "btn-success", true );
    fileInput.prop("disabled", true);

    // read images from archive
    archiveEntries = {};
    model.getEntries(files, function(entries) {
        fileSelect.innerHTML = "";
        // Filter directories away and process content
        entries.filter(function(entry) {
                return !entry.directory
            })
            .forEach(function(entry) {
                //var option = document.createElement("option");
                //option.text = entry.filename;
                var option = $('<option/>', {
                    text: entry.filename,
                    valie: entry.filename

                });
                option.appendTo(fileSelect);
                console.log(option);
                archiveEntries[entry.filename] = entry;

                //fileSelect.appendChild(option);
            });
    });
    $("#step-2").prop("hidden", false);
});



function labelingValidateButtons() {
    if (labelsPos == 0) {
        // if second parameter is true, class is added, removed otherwised
        btnLabelingPrev.toggleClass('btn-secondary', true);
        return;
    }

    if (labelsPos >= (labelsTotal)) {
        btnLabelingNext.toggleClass('btn-secondary', true);
        labelsPos -= 1;
        $("#btn-labeling-done").prop("hidden", false)
        return;
    }
    btnLabelingPrev.toggleClass('btn-secondary', false);
    btnLabelingNext.toggleClass('btn-secondary', false);

}



function labelingDone() {
    $("#text-captcha").prop("disabled", true);
    $("#step-3").prop('hidden', false);
    fileSelectChanged();;
}


function labelingCancel() {
    console.log("cancel labeling");
    labels = undefined;
    $("#step-2-labeling").prop("hidden", true);
    $("#step-3").prop('hidden', false);
    fileSelectChanged();
}

function labelingStart() {
    console.log("start labeling");
    labelingValidateButtons();
    $("#step-2-labeling").prop("hidden", false);
    $("#text-captcha").prop("disabled", false);
    $("#text-captcha").focus();
    labelsTotal = Object.keys(archiveEntries).length;
    labelsPos = 0;
    labels = {}
    $("#lbl-labeling-total").text(labelsTotal);
    labelingValidateButtons();
    labelingImageForCurrentPos();

}

function labelingImageForCurrentPos() {
    $("#lbl-labeling-current").text(labelsPos + 1);
    // Error, image out of range
    if (! ((0 <= labelsPos) && (labelsPos < labelsTotal))){
        return
    }
    model.getBlobFromEntry(Object.values(archiveEntries)[labelsPos],
        function(blob) {
            console.log(blob);
            var imageUrl = URL.createObjectURL(blob);
            $("#img-captcha-label").attr("src", imageUrl);
        });
}


function labelingImageNext() {
    console.log("next image");
    if (labelsPos >= (labelsTotal)){
        console.log("end of labeling...")
        return
    }
    if ($("#text-captcha").val() == "") {
        console.log("empty text")
        $("#text-captcha").focus()
        return;
    }
    labels[Object.keys(archiveEntries)[labelsPos]] = $("#text-captcha").val();
    labelsPos += 1
    labelingValidateButtons();
    labelingImageForCurrentPos();
    $("#text-captcha").val(labels[Object.keys(archiveEntries)[labelsPos]])
    $("#text-captcha").focus()

}

function labelingImagePrev() {
    console.log("prev image");

    if (labelsPos === 0){
        console.log("cant go back...")
        return;
    }
    labels[Object.keys(archiveEntries)[labelsPos]] = $("#text-captcha").val();
    labelsPos -= 1;
    labelingValidateButtons();
    labelingImageForCurrentPos();
    $("#text-captcha").val(labels[Object.keys(archiveEntries)[labelsPos]])
    $("#text-captcha").focus()
}

$("#text-captcha").keypress(function(e) {
    if (e.which == 13) {
        console.log("enter")
        labelingImageNext()
        return false; //<---- Add this line
    }
});
