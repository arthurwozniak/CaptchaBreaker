
from flask import Blueprint, render_template, flash
from flask import current_app, redirect, request, url_for, jsonify

from captchabreakerweb import dataset_extractor
from captchabreakerweb import modifier
from captchabreakerweb.admin import image_parser

admin = Blueprint('admin', __name__, template_folder='templates')

@admin.route('/')
def index():
    return redirect(url_for('admin.overview'))


@admin.route('/overview/')
def overview():
    return render_template('overview.html')


@admin.route('/datasets/')
def datasets():
    return render_template('datasets.html')


@admin.route('/datasets/new/')
def datasets_new():
    return render_template('datasets_new.html', operations=image_parser.get_operations())


@admin.route('/clasificators/')
def clasificators():
    return render_template('clasificators.html')


@admin.route('/datasets/new/preview', methods=['GET', 'POST'])
def preview():
    operations = ["grayscale", "treshold", "filter", "unmask"]
    result = {}

    print(request.json)
    print(request.json.keys())
    encoded_image = request.json.get("image")

    last_img = modifier.blob_to_img(encoded_image)
    todo = request.json.get("operations")
    print(todo)

    if "grayscale" in todo.keys():
        last_img = modifier.img_grayscale(last_img)
        result["grayscale"] = modifier.img_to_base64(last_img)

    if "filter" in todo.keys():
        last_img = modifier.img_filter(last_img, todo["filter"]["lower"], todo["filter"]["upper"])
        result["filter"] = modifier.img_to_base64(last_img)

    if "treshold" in todo.keys():
        last_img = modifier.img_treshhold(last_img)
        result["treshold"] = modifier.img_to_base64(last_img)

    if "unmask" in todo.keys():
        last_img = modifier.img_unmask(last_img, todo["unmask"]["count"])[0]
        result["unmask"] = modifier.img_to_base64(last_img)

    print(result.keys())
    for i in result.keys():
        print(result[i][:30])
    #print(response)
    return jsonify(result)


@admin.route('/datasets/new/upload', methods=['GET', 'POST'])
def upload():
    print(request.json.keys())
    #print(dataset_extractor.zip_from_base(request.json.get("file")))
    #print(request.json.get("operations"))
    archive = request.json.get("file")
    operations = request.json.get("operations")
    name = "testing"
    labels = request.json.get("labels", None)
    extractor = dataset_extractor.DatasetExtractor(archive, operations, name, labels)
    res = extractor.process_zip()
    print(res.keys())
    return "{}"
