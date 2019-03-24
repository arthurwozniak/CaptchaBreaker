from flask import Blueprint, render_template, request, jsonify, send_file

from captchabreaker import modifier
from captchabreaker.image_processing.captcha_decoder import CaptchaDecoder
from captchabreaker.models import ClassificatorModel, QueryModel, db

import random
import base64
import io

blueprint = Blueprint('demo', __name__, template_folder='templates', static_folder='static')


@blueprint.route('/')
def index():
    return render_template('demo/index.html', classificators=ClassificatorModel.finished())


@blueprint.route('/<int:classificator_id>/random_image/')
def random_image(classificator_id):
    images = ClassificatorModel.query.get(classificator_id).dataset.original_images
    random_image = random.choice(images)
    binary = base64.b64decode(random_image.data)
    return send_file(
        io.BytesIO(binary),
        mimetype='image/jpeg',
        as_attachment=False,
        attachment_filename='%s.png' % random_image.text)

@blueprint.route('/decode', methods=['POST'])
def decode():
    image_data = request.json.get("image")
    image = modifier.blob_to_img(image_data)
    classificator = ClassificatorModel.query.get(request.json.get('dataset-id'))
    decoder = CaptchaDecoder(image, classificator)
    log_request(classificator)
    return make_response(decoder.result(), "success")


def make_response(message, status):
    return jsonify({"message": message,
                    "status": status})


def log_request(classificator):
    query = QueryModel(classificator_id=classificator.id)
    db.session.add(query)
    db.session.commit()
