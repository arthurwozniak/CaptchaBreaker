from .operations import operations, parameters


def parse_args(args_json):
    args = {}
    for arg_json in args_json:
        arg = find_parameter(arg_json.get("class", None))
        if 'value' in arg_json.keys():
            arg.__setattr__('value', int(arg_json.get('value', 0)))
        elif 'type' in arg_json.keys():
            arg.__setattr__('type', str(arg_json.get('type')))
        args[arg_json.get('name')] = arg
    return args


def parse_operations(operations_json):
    operations = []
    for op_json in operations_json:
        op = find_operation(op_json.get("class", None))
        args = parse_args(op_json.get("args", []))
        for key in args.keys():
            op.__setattr__(key, args[key])
        operations.append(op)
    return operations


def find_operation(operation_name):
    for operation in operations():
        if operation.__class__.__name__ == operation_name:
            return operation


def find_parameter(parameter_name):
    for parameter in parameters():
        if parameter.__class__.__name__ == parameter_name:
            return parameter
