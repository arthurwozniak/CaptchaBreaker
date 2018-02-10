from .AbstractParserOperation import AbstractParserOperation


class Closing(AbstractParserOperation):

    _custom_name = "Morphological closing"

    def __init__(self):
        super(Closing, self).__init__()