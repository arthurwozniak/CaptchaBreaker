from .AbstractParserOperation import AbstractParserOperation
import cv2

class Inverse(AbstractParserOperation):
    _custom_name = "Inverse"

    def __init__(self):
        super(Inverse, self).__init__()

    def apply(self, image):
        image = image.copy()
        return cv2.bitwise_not(image)
