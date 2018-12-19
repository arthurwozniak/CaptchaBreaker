from flask import Blueprint, render_template, flash
from flask import current_app, redirect, request, url_for, jsonify

from datetime import datetime, timedelta

from sqlalchemy import and_

from captchabreaker import dataset_extractor
from captchabreaker import modifier
from captchabreaker.admin import image_parser
from captchabreaker.admin.image_parser import *
from captchabreaker.models import DatasetModel, OriginalImageModel, db, ClassificatorModel, QueryModel

from collections import Counter

admin = Blueprint('admin', __name__, template_folder='templates', static_folder='static')


@admin.route('/')
def index():
    return redirect(url_for('admin.overview'))


@admin.route('/overview/')
def overview():
    classifiers = ClassificatorModel.query.filter_by(is_finished=False).all()
    dataset_count = DatasetModel.query.count()
    classifiers_count = ClassificatorModel.query.count()
    total_count = QueryModel.query.count()
    delta = d = datetime.today() - timedelta(days=1)
    last_day_count = QueryModel.query.filter(QueryModel.created_at >= delta).count()
    return render_template('overview/index.html', classifiers=classifiers, stats={'datasets': dataset_count,
                                                                                  'classifiers': classifiers_count,
                                                                                  'total_count': total_count,
                                                                                  'last_day_count': last_day_count})


@admin.route('/datasets/')
def datasets():
    return render_template('datasets/index.html', datasets=DatasetModel.query.all())


@admin.route('/datasets/new/')
def datasets_new():
    return render_template('datasets/new.html', operations=image_parser.get_operations())


@admin.route('/datasets/<int:id>/')
def datasets_detail(id):
    dataset = DatasetModel.query.get(id)
    characters = ''.join([image.text for image in dataset.original_images])
    images_count = len(dataset.original_images)
    if dataset is None:
        return redirect(url_for('admin.datasets'))
    return render_template('datasets/show.html', dataset=dataset, images_count=images_count)


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


@admin.route('/datasets/<int:id>/delete/', methods=['POST'])
def dataset_delete(id):
    dataset = DatasetModel.query.get(id)
    db.session.delete(dataset)
    db.session.commit()
    return redirect(url_for('admin.datasets'))


@admin.route('/clasificators/')
def clasificators():
    classifiers = ClassificatorModel.query.all()
    return render_template('clasificators/index.html', classifiers=classifiers)


@admin.route('/clasificators/new/', methods=['GET'])
def clasificators_new():
    return render_template('clasificators/new.html', datasets=DatasetModel.query.all())


@admin.route('/clasificators/new/', methods=['POST'])
def clasificators_new_upload():
    from captchabreaker.tasks.process_dataset import training_task
    print(request.form)
    name = request.form.get('name')
    dataset_id = request.form.get('dataset', default=0, type=int)
    accuracy = request.form.get('accuracy', default=0, type=int)
    iterations = request.form.get('max-iterations', default=20, type=int)
    # return render_template('index.html', datasets=DatasetModel.query.all())
    task = training_task.delay(name, dataset_id, accuracy, iterations)
    return redirect(url_for('admin.overview'))


@admin.route('/clasificators/<int:id>/')
def classificators_detail(id):
    classifier = ClassificatorModel.query.get(id)
    if classifier is None:
        return redirect(url_for('admin.clasificators'))
    return render_template('clasificators/show.html', classifier=classifier)


@admin.route('/clasificators/<int:id>/delete/', methods=['POST'])
def classificators_delete(id):
    classifier = ClassificatorModel.query.get(id)
    if classifier:
        db.session.delete(classifier)
        db.session.commit()
    return redirect(url_for('admin.clasificators'))


@admin.route('/longtask')
def longtask():
    from captchabreaker.tasks.process_dataset import long_task, short_task
    task = long_task.apply_async()
    print(task.id)
    return jsonify({}), 202, {'Location': url_for('admin.taskstatus',
                                                  task_id=task.id)}


@admin.route('/status/<task_id>')
def taskstatus(task_id):
    from captchabreaker.tasks.process_dataset import long_task, short_task
    task = long_task.AsyncResult(task_id)
    if task.state == 'PENDING':
        # job did not start yet
        response = {
            'state': task.state,
            'current_iteration': 0,
            'max_iterations': 1,
            'status': 'Pending...'
        }
    elif task.state != 'FAILURE':
        print(task.info)
        response = {
            'state': task.state,
            'current_iteration': task.info.get('current_iteration', 0),
            'max_iterations': task.info.get('max_iterations', 1),
            'loss': task.info.get('loss', 0)
        }
        if 'result' in task.info:
            response['result'] = task.info['result']
    else:
        # something went wrong in the background job
        response = {
            'state': task.state,
            'current_iteration': 1,
            'max_iterations': 1,
            'status': str(task.info),  # this is the exception raised
        }
    return jsonify(response)
