
from flask import Blueprint, render_template, flash
from flask import current_app, redirect, request, url_for, jsonify

from captchabreakerweb import dataset_extractor
from captchabreakerweb import modifier
from captchabreakerweb.admin import image_parser
from captchabreakerweb.admin.image_parser import *
from captchabreakerweb.models import DatasetModel, OriginalImageModel, db

from collections import Counter


admin = Blueprint('admin', __name__, template_folder='templates', static_folder='static')

@admin.route('/')
def index():
    return redirect(url_for('admin.overview'))


@admin.route('/overview/')
def overview():
    return render_template('overview.html')


@admin.route('/datasets/')
def datasets():

    return render_template('datasets.html', datasets=DatasetModel.query.all())


@admin.route('/datasets/new/')
def datasets_new():
    return render_template('datasets_new.html', operations=image_parser.get_operations())

@admin.route('/datasets/<int:id>/')
def datasets_detail(id):
    dataset = DatasetModel.query.get(id)
    characters = ''.join([image.text for image in dataset.original_images])
    images_count = len(dataset.original_images)
    if dataset is None:
        return redirect(url_for('admin.datasets'))
    return render_template('datasets_detail.html', dataset=dataset, images_count=images_count)

@admin.route('/clasificators/')
def clasificators():
    return render_template('clasificators.html')

@admin.route('/datasets/new/preview2', methods=['GET', 'POST'])
def preview2():
    print(request.json)
    print(type(request.json))
    operations = parse_operations(request.json.get('operations', []))
    print(operations)
    encoded_image = request.json.get("image")

    last_img = modifier.blob_to_img(encoded_image)

    images = [last_img]
    for op in operations:
        images.append(op.apply(images[-1]))
    images.append(modifier.img_unmask(images[-1], request.json.get('count')))
    result_images = [modifier.img_to_base64(img) for img in images[1:]]
    names = [op.__class__.__name__ for op in operations]
    names.append("Extracted")
    return jsonify(list(zip(names, result_images)))

@admin.route('/datasets/new/upload', methods=['GET', 'POST'])
def upload():
    print(request.json.keys())
    #print(dataset_extractor.zip_from_base(request.json.get("file")))
    #print(request.json.get("operations"))
    archive = request.json.get("file")
    operations = parse_operations(request.json.get('operations', []))
    name = request.json.get("fileName")
    labels = request.json.get("labels", None)
    count = request.json.get("count", 0)
    extractor = dataset_extractor.DatasetExtractor(archive, operations, name, count, request.json.get('operations'), labels)
    try:
        res = extractor.process_and_save()
    except Exception as e:
        return jsonify({'status': 'error',
                        'message': str(e)})
    return jsonify({'status': 'success',
                    'id': res.id})

@admin.route('/datasets/<int:id>/delete/', methods=['POST'])
def dataset_delete(id):
    dataset = DatasetModel.query.get(id)
    db.session.delete(dataset)
    db.session.commit()
    return redirect(url_for('admin.datasets'))