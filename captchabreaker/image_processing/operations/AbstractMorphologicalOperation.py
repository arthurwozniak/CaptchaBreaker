from .AbstractParserOperation import AbstractParserOperation
from captchabreaker.image_processing.operations.parameters.Integer import Integer


class AbstractMorphologicalOperation(AbstractParserOperation):

    _custom_name = "Abstract Morphological closing"

    def __init__(self):
        super(AbstractMorphologicalOperation, self).__init__()
        self.kernel_size = Integer(value=5, min=1, max=10, name="kernel_size")

    def __str__(self):
        return "[{0}; kernel_size: {1}]".format(self.__class__.__name__, self.kernel_size)
