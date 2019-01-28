from flask import Blueprint, render_template, request, jsonify

from captchabreaker import modifier
from captchabreaker.image_processing.captcha_decoder import CaptchaDecoder
from captchabreaker.models import ClassificatorModel, QueryModel, db

blueprint = Blueprint('demo', __name__, template_folder='templates', static_folder='static')


@blueprint.route('/')
def index():
    return render_template('demo/index.html', classificators=ClassificatorModel.finished())


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
