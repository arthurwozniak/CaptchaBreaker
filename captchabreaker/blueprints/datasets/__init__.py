from captchabreaker.blueprints.helper import get_blueprint_for
from flask import redirect, request, url_for, jsonify
from flask import render_template
from captchabreaker import dataset_extractor
from captchabreaker import modifier
from captchabreaker.admin import image_parser
from captchabreaker.admin.image_parser import *
from captchabreaker.models import DatasetModel, db

blueprint = get_blueprint_for(DatasetModel)

@blueprint.route('/')
def index():
    return render_template('datasets/index.html', datasets=DatasetModel.query.all())


@blueprint.route('/new/')
def datasets_new():
    return render_template('datasets/new.html', operations=image_parser.get_operations())


@blueprint.route('/<int:id>/')
def datasets_detail(id):
    dataset = DatasetModel.query.get(id)
    characters = ''.join([image.text for image in dataset.original_images])
    images_count = len(dataset.original_images)
    if dataset is None:
        return redirect(url_for('admin.datasets'))
    return render_template('datasets/show.html', dataset=dataset, images_count=images_count)


@blueprint.route('/new/preview2', methods=['GET', 'POST'])
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


@blueprint.route('/new/upload', methods=['GET', 'POST'])
def upload():
    print("FO")
    print(request.json.keys())
    # print(dataset_extractor.zip_from_base(request.json.get("file")))
    # print(request.json.get("operations"))
    archive = request.json.get("file")
    print("FO")
    operations = parse_operations(request.json.get('operations', []))
    print("FO")
    name = request.json.get("fileName")
    print("FO")
    labels = request.json.get("labels", None)
    count = request.json.get("count", 0)
    extractor = dataset_extractor.DatasetExtractor(archive, operations, name, count, request.json.get('operations'),
                                                   labels)
    try:
        res = extractor.process_and_save()
    except Exception as e:
        return jsonify({'status': 'error',
                        'message': str(e)})
    return jsonify({'status': 'success',
                    'id': res.id})


@blueprint.route('/<int:id>/delete/', methods=['POST'])
def dataset_delete(id):
    dataset = DatasetModel.query.get(id)
    db.session.delete(dataset)
    db.session.commit()
    return redirect(url_for('admin.datasets'))