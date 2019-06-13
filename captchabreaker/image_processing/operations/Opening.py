from .AbstractMorphologicalOperation import AbstractMorphologicalOperation
import numpy as np
import cv2

class Opening(AbstractMorphologicalOperation):
    _custom_name = "Morphological opening"

    def __init__(self):
        super(Opening, self).__init__()

    def apply(self, image):
        image = image.copy()
        kernel = self.__structure_element__()
        return cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel, iterations=self.__get_iterations__())