from .AbstractParserOperation import AbstractParserOperation

class Erosion(AbstractParserOperation):
    _custom_name = "Morphological erosion"

    def __init__(self):
        super(Erosion, self).__init__()