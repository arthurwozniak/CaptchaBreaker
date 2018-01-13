var archiveEntries;
var allowedFileTypes = ["png", "jpg", "jpeg", "bmp"]
var labels;
var labelsTotal = 0;
var labelsPos = 0;

$("#wrapper-labeling").hide();
$("#wrapper-labeling-input").hide();
//$("#file-select").hide();


    var requestFileSystem = this.webkitRequestFileSystem || this.mozRequestFileSystem || this.requestFileSystem;
    var URL = this.webkitURL || this.mozURL || this.URL;


    function onerror(message) {
        alert(message);
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


    var fileInput = document.getElementById('file-input');
    var fileSelect = document.getElementById('file-select');
    var fileImg = document.getElementById('file-img');


    fileSelect.hidden = true;

    fileSelect.addEventListener('change', function() {

        console.log(fileSelect.value);
        model.getBlobFromEntry(archiveEntries[fileSelect.value],
        function(blob) {
            console.log(blob);
            var imageUrl = URL.createObjectURL(blob);
            fileImg.src = imageUrl;
            var xhr = new XMLHttpRequest();
            xhr.open("POST", "/foo", true);
            xhr.send(blob);
        } );

    }, false);

    fileInput.addEventListener('change', function() {
        // File selection was aborted
        if (!fileInput.files[0]) {
            return;
        }
        // User forced file-chooser to pick-up different file type
        if (fileInput.files[0].type !== "application/zip") {
            alert("Only ZIP files are allowed");
            fileInput.value = "";
            return;
        }
        fileInput.disabled = true;
        fileSelect.hidden = false;
        $("#wrapper-labeling").show();

        archiveEntries = {};
        model.getEntries(fileInput.files[0], function(entries) {
            fileSelect.innerHTML = "";
            // Filter directories away and process content
            entries.filter(function (entry){return !entry.directory})
                   .forEach(function(entry) {
                var option = document.createElement("option");
                option.text = entry.filename;

                archiveEntries[entry.filename] = entry;

                fileSelect.appendChild(option);
            });
        });
    }, false);




function labelingCancel() {
    console.log("cancel labeling");
    labels = undefined;
    $("#wrapper-labeling-input").hide();
}

function labelingStart() {
    console.log("start labeling");
    $("#wrapper-labeling-input").show();
    $("#text-captcha").focus();
    labelsTotal = Object.keys(archiveEntries).length;
    labelsPos = 0;
    labels = {}
    labelingImageForCurrentPos();

}

function labelingImageForCurrentPos(){
    model.getBlobFromEntry(Object.values(archiveEntries)[labelsPos],
    function(blob) {
        console.log(blob);
        var imageUrl = URL.createObjectURL(blob);
        $("#img-captcha-label").attr("src", imageUrl);
    } );
}

function labelingImageNext(){
    // TODO: hide btns when cant go forward
    if (labelsPos == (labelsTotal - 1)){

    }
    console.log("next image");
    labels[Object.keys(archiveEntries)[labelsPos]] = $("#text-captcha").val();
    labelsPos += 1;
    labelingImageForCurrentPos();
    $("#text-captcha").val("")
    $("#text-captcha").focus()

}

function labelingImagePrev() {
    console.log("prev image");
    labelsPos -= 1;
}

$("#text-captcha").keypress(function (e) {
  if (e.which == 13) {
    console.log("enter")
    labelingImageNext()
    return false;    //<---- Add this line
  }
});
