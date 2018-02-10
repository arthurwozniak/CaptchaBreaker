from .AbstractParserOperation import AbstractParserOperation

class Dilation(AbstractParserOperation):
    _custom_name = "Morphological dilation"

    def __init__(self):
        super(Dilation, self).__init__()