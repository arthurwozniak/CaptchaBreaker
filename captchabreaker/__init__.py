from celery import Celery
from flask import Flask

import captchabreaker.modifier
from captchabreaker import config
from captchabreaker.views.helper import parse_operations
from captchabreaker.dataset_extractor import DatasetExtractor
from captchabreaker.image_processing.classificators import CNN
from captchabreaker.models import db, ClassificatorModel, DatasetModel, QueryModel
from captchabreaker.utils import get_instance_folder_path, set_file_logger

from captchabreaker.views import blueprints

#from captchabreaker.admin import admin_blueprints

app = Flask(__name__, instance_path=get_instance_folder_path(), instance_relative_config=True)
app.config.from_object(config)
app.url_map.strict_slashes = False

set_file_logger(app)

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

from captchabreaker.tasks.process_dataset import long_task, short_task, training_task


db.init_app(app)

with app.test_request_context():
    db.create_all()

for blueprint in blueprints():
    app.register_blueprint(blueprint)