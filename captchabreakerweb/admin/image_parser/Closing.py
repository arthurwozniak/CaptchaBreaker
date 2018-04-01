from .AbstractMorphologicalOperation import AbstractMorphologicalOperation
import numpy as np
import cv2

class Closing(AbstractMorphologicalOperation):

    _custom_name = "Morphological closing"

    def __init__(self):
        super(Closing, self).__init__()

    def apply(self, image):
        image = image.copy()
        kernel = np.ones((int(self.kernel_size), int(self.kernel_size)), np.uint8)
        return cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)