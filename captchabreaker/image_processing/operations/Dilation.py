from .AbstractMorphologicalOperation import AbstractMorphologicalOperation
import numpy as np
import cv2


class Dilation(AbstractMorphologicalOperation):
    _custom_name = "Morphological dilation"

    def __init__(self):
        super(Dilation, self).__init__()

    def apply(self, image):
        image = image.copy()
        kernel = self.__structure_element__()
        return cv2.dilate(image, kernel, iterations=1)
