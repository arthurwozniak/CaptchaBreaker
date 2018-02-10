from .AbstractParserOperation import AbstractParserOperation

class TresholdCustom(AbstractParserOperation):

    _custom_name = "Custom treshold"

    
    def __init__(self):
        super(TresholdCustom, self).__init__()