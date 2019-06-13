from .AbstractParserOperation import AbstractParserOperation
from captchabreaker.image_processing.operations.parameters import Integer, KernelShape
import cv2


class AbstractMorphologicalOperation(AbstractParserOperation):

    _custom_name = "Abstract Morphological closing"

    def __init__(self):
        super(AbstractMorphologicalOperation, self).__init__()
        self.kernel_size = Integer(value=1, min=0, max=10, name="kernel_size")
        self.iterations = Integer(value=1, min=1, max=10, name="iterations")
        self.kernel_shape = KernelShape(name="kernel_shape")

    def __str__(self):
        return "[{0}; kernel_size: {1}]".format(self.__class__.__name__, self.kernel_size)

    def __get_kernel_size__(self):
        return int(self.kernel_size) * 2 + 1

    def __get_iterations__(self):
        return int(self.iterations)

    def __structure_element__(self):
        size = self.__get_kernel_size__()
        return cv2.getStructuringElement(self.kernel_shape.get_type(), (size, size))
