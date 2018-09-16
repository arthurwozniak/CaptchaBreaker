from flask import abort, Flask, g, render_template, request, jsonify
from celery import Celery
import json
import base64, pickle

from captchabreakerweb.utils import get_instance_folder_path
from captchabreakerweb.admin.views import admin, parse_operations
from captchabreakerweb.models import db, ClasificatorModel, DatasetModel, QueryModel

import captchabreakerweb.modifier
from captchabreakerweb.dataset_extractor import DatasetExtractor

from captchabreakerweb.ml.CNN import CNN
import numpy as np
import torch
from torch.autograd import Variable



app = Flask(__name__,
            instance_path=get_instance_folder_path(),
            instance_relative_config=True,
            template_folder='templates')

app.config['CELERY_BROKER_URL'] = 'redis://127.0.0.1:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://127.0.0.1:6379/0'

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

app.config['DEBUG'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'

from captchabreakerweb.tasks.process_dataset import long_task, short_task, training_task


db.init_app(app)

with app.test_request_context():
    db.create_all()


@app.errorhandler(404)
def page_not_found(error):
    app.logger.error('Page not found: %s', (request.path, error))
    return render_template('404.html'), 404
#
# @app.errorhandler(500)
# def internal_server_error(error):
#     app.logger.error('Server Error: %s', (error))
#     return render_template('500.htm'), 500
#
# @app.errorhandler(Exception)
# def unhandled_exception(error):
#     app.logger.error('Unhandled Exception: %s', (error))
#     return render_template('500.htm'), 500


@app.route('/')
def home(lang_code=None):
    print("home")
    return render_template('index.html', clasificators=ClasificatorModel.query.all())


@app.route('/decode', methods=['POST'])
def decode():
    print(request.json)
    encoded_image = request.json.get("image")

    last_img = modifier.blob_to_img(encoded_image)
    clasificator = ClasificatorModel.query.get(request.json.get('dataset-id'))
    if clasificator is None:
        return jsonify({"message": "Unknown classifier",
                        "status": "error"})
    dataset = DatasetModel.query.get(clasificator.dataset_id)

    import re
    operations = parse_operations(json.loads(re.sub("'", '"', dataset.extraction_config)))
    datasetExtractor = DatasetExtractor(None, operations, None, dataset.characters_per_image, None)
    characters = datasetExtractor.process_file(last_img)
    cnn = CNN(len(dataset.known_characters))
    cnn.load_state_dict(pickle.loads(base64.b64decode(clasificator.network)))
    characters = np.array(characters)
    characters = torch.from_numpy((characters.astype(dtype=np.float32)/255).reshape([5, 1, 20, 20]))
    data = Variable(characters)
    cnn.eval()
    output = cnn(data)
    pred = output.data.max(1, keepdim=True)[1]
    data = pred.squeeze().tolist()
    dataset_characters = dataset.known_characters
    data_str = "".join(map(lambda x: dataset_characters[x], data))
    query = QueryModel(classifier_id=clasificator.id)
    db.session.add(query)
    db.session.commit()

    return jsonify({"message": data_str,
                    "status": "success"})


app.register_blueprint(admin, url_prefix='/admin')
