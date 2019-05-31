from flask import Flask
from flask_simplelogin import SimpleLogin

import captchabreaker.modifier
from captchabreaker import config
from captchabreaker.views.helper import parse_operations, title_generator, is_current_blueprint
from captchabreaker.image_processing.dataset_extractor import DatasetExtractor
from captchabreaker.image_processing.classificators import CNN
from captchabreaker.models import db, ClassificatorModel, DatasetModel, QueryModel
from captchabreaker.helper import get_instance_folder_path, set_file_logger, format_datetime

from captchabreaker.views import blueprints
from captchabreaker.celery import make_celery

app = Flask(__name__, instance_path=get_instance_folder_path(), instance_relative_config=True)
app.config.from_object(config)
app.url_map.strict_slashes = False
SimpleLogin(app)
app.jinja_env.globals.update(title_generator=title_generator)
app.jinja_env.globals.update(is_current_blueprint=is_current_blueprint)
app.jinja_env.filters['datetime'] = format_datetime

set_file_logger(app)

celery = make_celery(app)

from captchabreaker.tasks.training_task import training_task


db.init_app(app)

with app.test_request_context():
    db.create_all()

for blueprint in blueprints():
    app.register_blueprint(blueprint)
