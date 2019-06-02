from captchabreaker.views.helper import get_blueprint_for
from flask import redirect, request, url_for, jsonify, send_file
from flask import render_template
from flask_simplelogin import login_required
from captchabreaker import modifier
from captchabreaker.image_processing import operations, dataset_extractor
from captchabreaker.image_processing import helper
from captchabreaker.models import DatasetModel, db, OriginalImageModel, CharacterModel
import base64
import io
import pprint
import random

blueprint = get_blueprint_for(DatasetModel)


@blueprint.route('/')
@login_required
def index():
    return render_template('datasets/index.html', datasets=DatasetModel.query.all())


@blueprint.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    if request.method == 'GET':
        return render_template('datasets/new.html', operations=operations.operations())
    return create()


def create():
    archive = request.json.get("file")
    operations = helper.parse_operations(request.json.get('operations', []))
    name = request.json.get("fileName")
    labels = request.json.get("labels", None)
    count = request.json.get("count", 0)
    extractor = dataset_extractor.DatasetExtractor(archive, operations, name, count, request.json.get('operations'),
                                                   labels)
    try:
        res = extractor.perform()
    except Exception as e:
        return jsonify({'status': 'error',
                        'message': str(e)})
    return jsonify({'status': 'success',
                    'id': res.id})


@blueprint.route('/<int:id>/')
@login_required
def show(id):
    dataset = DatasetModel.query.get(id)
    if dataset is None:
        return redirect(url_for('admin.datasets'))
    images_count = len(dataset.original_images)
    return render_template('datasets/show.html', dataset=dataset, images_count=images_count)


@blueprint.route('/<int:dataset_id>/image/<int:image_id>/')
@login_required
def image(dataset_id, image_id):
    image = OriginalImageModel.query.get(image_id)
    binary = base64.b64decode(image.data)
    return send_file(
        io.BytesIO(binary),
        mimetype='image/jpeg',
        as_attachment=True,
        attachment_filename='%s.png' % image.text)


@blueprint.route('/<int:dataset_id>/character/<int:character_id>/')
@login_required
def character(dataset_id, character_id):
    image = CharacterModel.query.get(character_id)
    binary = base64.b64decode(image.image)
    return send_file(
        io.BytesIO(binary),
        mimetype='image/bmp',
        as_attachment=True,
        attachment_filename='%s.bmp' % image.character)


@blueprint.route('/preview', methods=['GET', 'POST'])
@login_required
def preview():
    operations = helper.parse_operations(request.json.get('operations', []))
    image_encoded = request.json.get("image")

    image_input = modifier.blob_to_img(image_encoded)

    images = [image_input]
    for op in operations:
        images.append(op.apply(images[-1]))
    images.append(modifier.img_unmask(images[-1], request.json.get('count')))
    result_images = [modifier.img_to_base64(img) for img in images[1:]]
    names = [op.__class__.__name__ for op in operations]
    names.append("Extracted")
    return jsonify(list(zip(names, result_images)))


@blueprint.route('/<int:id>/delete/', methods=['POST'])
@login_required
def delete(id):
    dataset = DatasetModel.query.get(id)
    if dataset:
        db.session.delete(dataset)
        db.session.commit()
    return redirect(url_for('dashboard.datasets.index'))
