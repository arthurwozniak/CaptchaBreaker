from .AbstractParserOperation import AbstractParserOperation

class Opening(AbstractParserOperation):
    _custom_name = "Morphological opening"

    def __init__(self):
        super(Opening, self).__init__()