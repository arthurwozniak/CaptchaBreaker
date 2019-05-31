from .AbstractParserOperation import AbstractParserOperation
from captchabreaker.image_processing.operations.parameters.Integer import Integer
import cv2
import numpy as np

class AreaFilter(AbstractParserOperation):
    _custom_name = "Area Filter"

    def __init__(self):
        super(AreaFilter, self).__init__()
        self.size = Integer(value=2, min=0, max=65536, name="size")

    def __str__(self):
        return "[{0}; size: {1}]".format(self.__class__.__name__, self.size)

    def apply(self, image):
        image = image.copy()
        area_size = self.size.value
        mask = self.prepare_invalid_contours(image, area_size)
        image = cv2.bitwise_and(image, image, mask=mask)
        return image

    def prepare_invalid_contours(self, image, area_size):
        mask = np.ones(image.shape[:2], dtype="uint8") * 255
        contours, hierarchy = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = [contour for contour in contours if cv2.contourArea(contour) <= area_size]
        for i in contours:
            cv2.drawContours(mask, [i], -1, 0, -1)
        return mask