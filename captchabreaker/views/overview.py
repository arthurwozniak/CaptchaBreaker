from flask import Blueprint, redirect, url_for, render_template
from datetime import datetime, timedelta
from captchabreaker.models import DatasetModel, OriginalImageModel, db, ClassificatorModel, QueryModel

blueprint = Blueprint('dashboard.overview', __name__, template_folder='templates', static_folder='static', url_prefix='/dashboard')


@blueprint.route('/')
def index():
    classificators = ClassificatorModel.query.filter_by(is_finished=False).all()
    dataset_count = DatasetModel.query.count()
    classificators_count = ClassificatorModel.query.count()
    total_count = QueryModel.query.count()
    delta = datetime.today() - timedelta(days=1)
    last_day_count = QueryModel.query.filter(QueryModel.created_at >= delta).count()
    return render_template('overview/index.html', classificators=classificators, stats={'datasets': dataset_count,
                                                                                  'classificators': classificators_count,
                                                                                  'total_count': total_count,
                                                                                  'last_day_count': last_day_count})