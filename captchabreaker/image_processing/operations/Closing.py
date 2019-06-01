from .AbstractMorphologicalOperation import AbstractMorphologicalOperation
import numpy as np
import cv2


class Closing(AbstractMorphologicalOperation):
    _custom_name = "Morphological closing"

    def __init__(self):
        super(Closing, self).__init__()

    def apply(self, image):
        image = image.copy()
        kernel = self.__structure_element__()
        return cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)
