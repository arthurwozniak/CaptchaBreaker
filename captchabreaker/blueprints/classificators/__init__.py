from captchabreaker.blueprints.helper import *
from captchabreaker.models import ClassificatorModel, DatasetModel
from flask import g

from flask import render_template, request, redirect, url_for

blueprint = get_blueprint_for(ClassificatorModel)
@blueprint.route('/')
def index():
    classifiers = ClassificatorModel.query.all()
    return render_template('classificators/index.html', classifiers=classifiers)


@blueprint.route('/new/', methods=['GET'])
def clasificators_new():
    return render_template('classificators/new.html', datasets=DatasetModel.query.all())


@blueprint.route('/new/', methods=['POST'])
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


@blueprint.route('/<int:id>/')
def classificators_detail(id):
    classifier = ClassificatorModel.query.get(id)
    if classifier is None:
        return redirect(url_for('admin.clasificators'))
    return render_template('clasificators/show.html', classifier=classifier)


@blueprint.route('/<int:id>/delete/', methods=['POST'])
def classificators_delete(id):
    classifier = ClassificatorModel.query.get(id)
    if classifier:
        g.db.session.delete(classifier)
        g.db.session.commit()
    return redirect(url_for('admin.clasificators'))
