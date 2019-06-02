from flask import Blueprint
from captchabreaker.image_processing.helper import parse_args
from captchabreaker import config
from pprint import pformat


def get_blueprint_for(model):
    tablename = model.__tablename__
    return Blueprint('dashboard.{}'.format(tablename), __name__, template_folder='{}/templates'.format(tablename),
                     static_folder='static', url_prefix='/dashboard/{}'.format(tablename))


def parse_operations(operations_json):
    operations = []
    for op_json in operations_json:
        print(op_json)
        op = globals()[op_json.get("class", None)]()
        args = parse_args(op_json.get("args", []))
        for key in args.keys():
            op.__setattr__(key, args[key])
        operations.append(op)
    return operations


def is_current_blueprint(request, blueprint_name):
    return request.blueprint.endswith(blueprint_name)


def title_generator(location=None):
    if location:
        return "{} - {}".format(config.HTML_TITLE, location)
    else:
        return config.HTML_TITLE


def pretty_print(json):
    return pformat(json)
