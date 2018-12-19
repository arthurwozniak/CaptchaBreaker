from .AbstractParserOperation import AbstractParserOperation
import cv2

class Grayscale(AbstractParserOperation):
    _custom_name = "Grayscale"

    def __init__(self):
        super(Grayscale, self).__init__()

    def apply(self, image):
        image = image.copy()
        # Image has 3 channels
        if len(image.shape) == 3:
            return cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        return image