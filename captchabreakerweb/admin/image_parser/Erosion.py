from .AbstractMorphologicalOperation import AbstractMorphologicalOperation
import numpy as np
import cv2

class Erosion(AbstractMorphologicalOperation):
    _custom_name = "Morphological erosion"

    def __init__(self):
        super(Erosion, self).__init__()

    def apply(self, image):
        image = image.copy()
        kernel = np.ones((int(self.kernel_size), int(self.kernel_size)), np.uint8)
        return cv2.erode(image,kernel,iterations = 1)