from .helper import *
from captchabreaker.models import ClassificatorModel, DatasetModel
from flask import g

from flask import render_template, request, redirect, url_for

blueprint = get_blueprint_for(ClassificatorModel)
@blueprint.route('/')
def index():
    classificator = ClassificatorModel.query.all()
    return render_template('classificators/index.html', classificator=classificator)


@blueprint.route('/new/', methods=['GET', 'POST'])
def new():
    if request.method == 'GET':
        return render_template('classificators/new.html', datasets=DatasetModel.query.all())
    return create()

def create():
    from captchabreaker.tasks.process_dataset import training_task
    print(request.form)
    name = request.form.get('name')
    dataset_id = request.form.get('dataset', default=0, type=int)
    accuracy = request.form.get('accuracy', default=0, type=int)
    iterations = request.form.get('max-iterations', default=20, type=int)
    # return render_template('index.html', datasets=DatasetModel.query.all())
    task = training_task.delay(name, dataset_id, accuracy, iterations)
    # TODO: fix celery communication
    return redirect(url_for('dashboard.overview.index'))


@blueprint.route('/<int:id>/')
def show(id):
    classificator = ClassificatorModel.query.get(id)
    if classificator is None:
        return redirect(url_for('dashboard.classificators.index'))
    return render_template('classificators/show.html', classificator=classificator)


@blueprint.route('/<int:id>/delete/', methods=['POST'])
def delete(id):
    classificator = ClassificatorModel.query.get(id)
    if classificator:
        g.db.session.delete(classificator)
        g.db.session.commit()
    return redirect(url_for('dashboard.classificators.index'))
