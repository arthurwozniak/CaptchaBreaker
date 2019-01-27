from flask import Blueprint, render_template, jsonify
from datetime import datetime, timedelta
from captchabreaker.models import DatasetModel, ClassificatorModel, QueryModel
from flask_simplelogin import login_required
from celery import states
from celery.result import AsyncResult

blueprint = Blueprint('dashboard.overview', __name__, template_folder='templates', static_folder='static',
                      url_prefix='/dashboard')


@blueprint.route('/')
@login_required
def index():
    classificators = ClassificatorModel.query.filter_by(is_finished=False).all()
    datasets_count = DatasetModel.query.count()
    classificators_count = ClassificatorModel.query.count()
    total_count = QueryModel.query.count()
    delta = datetime.today() - timedelta(days=1)
    last_day_count = QueryModel.query.filter(QueryModel.created_at >= delta).count()
    return render_template('overview/index.html', classificators=classificators, stats={'datasets': datasets_count,
                                                                                        'classificators': classificators_count,
                                                                                        'total_count': total_count,
                                                                                        'last_day_count': last_day_count})


@blueprint.route('/task_status/<classificator_id>')
@login_required
def taskstatus(classificator_id):
    task_id = ClassificatorModel.query.get(classificator_id).task_id
    task = AsyncResult(ClassificatorModel.query.get(classificator_id).task_id)
    info_dict = task.info or {}
    return jsonify({
        'state': task.state,
        'current_iteration': info_dict.get('current_iteration', 0),
        'max_iterations': info_dict.get('max_iterations', 1),
        'status': str(info_dict),
        'loss': info_dict.get('loss', 0),
        'result': info_dict.get('result', '')
    })
