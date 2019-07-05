from .AbstractParserOperation import AbstractParserOperation
from captchabreaker.image_processing.operations.parameters.Integer import Integer
import cv2

class Scale(AbstractParserOperation):
    _custom_name = "Scale"

    def __init__(self):
        super(Scale, self).__init__()
        self.scale_ratio = Integer(value=1, min=0, max=255, name="scale_ratio")

    def apply(self, image):
        image = image.copy()
        scale_ratio = self.scale_ratio.value
        return cv2.resize(image, (0,0), fx=scale_ratio, fy=scale_ratio)
