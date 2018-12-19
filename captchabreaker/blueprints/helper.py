from flask import Blueprint
from captchabreaker.admin.image_parser import parse_args


def get_blueprint_for(model):
    tablename = model.__tablename__
    return Blueprint('admin.{}'.format(tablename), __name__, template_folder='{}/templates'.format(tablename),
                     static_folder='static/{}'.format(tablename), url_prefix='/admin/{}'.format(tablename))

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

