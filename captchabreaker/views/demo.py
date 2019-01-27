import os

from flask import Blueprint, send_from_directory, render_template, request, current_app
from captchabreaker.models import ClassificatorModel
from captchabreaker.config import MODEL_DIRECTORY

blueprint = Blueprint('demo', __name__, template_folder='templates', static_folder='static')


@blueprint.route('/')
def index():
    return render_template('demo/index.html', classificators=ClassificatorModel.query.all())


@blueprint.route('/decode', methods=['POST'])
def decode():
    from captchabreaker import modifier
    from flask import jsonify
    from captchabreaker.models import DatasetModel, db, QueryModel
    from captchabreaker.image_processing.dataset_extractor import DatasetExtractor
    from captchabreaker.image_processing.classificators.cnn import CNN
    import numpy as np
    import torch
    import base64, pickle
    import json
    from torch.autograd.variable import Variable
    from captchabreaker.image_processing.helper import parse_operations

    print(request.json)
    encoded_image = request.json.get("image")

    last_img = modifier.blob_to_img(encoded_image)
    classificator = ClassificatorModel.query.get(request.json.get('dataset-id'))
    if classificator is None:
        return jsonify({"message": "Unknown classificator",
                        "status": "error"})
    dataset = DatasetModel.query.get(classificator.dataset_id)

    import re
    operations = parse_operations(json.loads(re.sub("'", '"', dataset.extraction_config)))
    datasetExtractor = DatasetExtractor(None, operations, None, dataset.characters_per_image, None)
    characters = datasetExtractor.process_file(last_img)
    cnn = CNN(len(dataset.known_characters))
    path = os.path.join(MODEL_DIRECTORY, classificator.task_id)
    cnn.load_state_dict(torch.load(path))
    characters = np.array(characters)
    characters = torch.from_numpy((characters.astype(dtype=np.float32) / 255).reshape([5, 1, 20, 20]))
    data = Variable(characters)
    cnn.eval()
    output = cnn(data)
    pred = output.data.max(1, keepdim=True)[1]
    data = pred.squeeze().tolist()
    dataset_characters = dataset.known_characters
    data_str = "".join(map(lambda x: dataset_characters[x], data))
    query = QueryModel(classificator_id=classificator.id)
    db.session.add(query)
    db.session.commit()

    return jsonify({"message": data_str,
                    "status": "success"})
