import inspect
import sys

from .Closing import Closing
from .Dilation import Dilation
from .Erosion import Erosion
from .Grayscale import Grayscale
from .Opening import Opening
from .TresholdCustom import TresholdCustom
from .TresholdOtsu import TresholdOtsu
from .ParameterInteger import ParameterInteger
from .Inverse import Inverse

def get_operations():
    operations = []
    for name, obj in inspect.getmembers(sys.modules[__name__]):
        if inspect.isclass(obj) and obj != ParameterInteger:
            operations.append(obj())
    return sorted(operations, key=lambda op: op.name)


def parse_args(args_json):
    args = {}
    for arg_json in args_json:
        print(arg_json.get("class", None))
        print(globals()[arg_json.get("class", None)])
        print(globals()[arg_json.get("class", None)]())
        arg = globals()[arg_json.get("class", None)]()
        if 'value' in arg_json.keys():
            arg.__setattr__('value', int(arg_json.get('value', 0)))
        args[arg_json.get('name')] = arg
    return args


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