from flask import Blueprint, redirect, url_for, render_template
from datetime import datetime, timedelta
from captchabreaker.models import DatasetModel, OriginalImageModel, db, ClassificatorModel, QueryModel

blueprint = Blueprint('admin.overview', __name__, template_folder='templates', static_folder='static', url_prefix='/admin')


@blueprint.route('/')
def index():
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