import base64
import json
import pickle

import numpy as np
import torch
from celery import Celery
from flask import Flask, request, jsonify
from torch.autograd import Variable

import captchabreaker.modifier
from captchabreaker import config
from captchabreaker.blueprints.helper import parse_operations
from captchabreaker.dataset_extractor import DatasetExtractor
from captchabreaker.ml.CNN import CNN
from captchabreaker.models import db, ClassificatorModel, DatasetModel, QueryModel
from captchabreaker.utils import get_instance_folder_path, set_file_logger
from captchabreaker.views import base_routes

from captchabreaker.blueprints import admin_blueprints

#from captchabreaker.admin import admin_blueprints

app = Flask(__name__, instance_path=get_instance_folder_path(), instance_relative_config=True)

app.config.from_object(config)

set_file_logger(app)

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

from captchabreaker.tasks.process_dataset import long_task, short_task, training_task


db.init_app(app)

with app.test_request_context():
    db.create_all()



@app.route('/decode', methods=['POST'])
def decode():
    print(request.json)
    encoded_image = request.json.get("image")

    last_img = modifier.blob_to_img(encoded_image)
    clasificator = ClassificatorModel.query.get(request.json.get('dataset-id'))
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


app.register_blueprint(base_routes)
for blueprint in admin_blueprints():
    app.register_blueprint(blueprint)
