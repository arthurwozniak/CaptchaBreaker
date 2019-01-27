from flask import g
from flask import render_template, request, redirect, url_for, jsonify
from flask_simplelogin import login_required

from captchabreaker.models import ClassificatorModel, DatasetModel, db
from .helper import *

blueprint = get_blueprint_for(ClassificatorModel)


@blueprint.route('/')
@login_required
def index():
    classificators = ClassificatorModel.query.all()
    return render_template('classificators/index.html', classificators=classificators)


@blueprint.route('/new/', methods=['GET', 'POST'])
@login_required
def new():
    if request.method == 'GET':
        return render_template('classificators/new.html', datasets=DatasetModel.query.all())
    return create()


def create():
    from captchabreaker.tasks.process_dataset import training_task
    params = classificator_parameters_from(request)
    print(params)
    classificator = ClassificatorModel(name=params['name'], dataset_id=params['dataset_id'], is_finished=False, config=params)
    db.session.add(classificator)
    db.session.commit()
    task = training_task.delay(classificator.id)
    # TODO: fix celery communication
    return redirect(url_for('dashboard.overview.index'))


@blueprint.route('/<int:id>/')
@login_required
def show(id):
    classificator = ClassificatorModel.query.get(id)
    if classificator is None:
        return redirect(url_for('dashboard.classificators.index'))
    return render_template('classificators/show.html', classificator=classificator)


@blueprint.route('/<int:id>/delete/', methods=['POST'])
@login_required
def delete(id):
    classificator = ClassificatorModel.query.get(id)
    if classificator:
        db.session.delete(classificator)
        db.session.commit()
    return redirect(url_for('dashboard.classificators.index'))


def classificator_parameters_from(request):
    return {
        'name': request.form.get('name'),
        'dataset_id': request.form.get('dataset', default=0, type=int),
        'accuracy': request.form.get('accuracy', default=0, type=int),
        'iterations': request.form.get('max-iterations', default=20, type=int)
    }