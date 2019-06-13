from .AbstractParserOperation import AbstractParserOperation
from captchabreaker.image_processing.operations.parameters.Integer import Integer
import cv2
import numpy as np

class AreaFilter(AbstractParserOperation):
    _custom_name = "Area Filter"

    def __init__(self):
        super(AreaFilter, self).__init__()
        self.area= Integer(value=2, min=0, max=255, name="area")
        self.height = Integer(value=2, min=0, max=255, name="height")

    def __str__(self):
        return "[{0}; area: {1}, height: {2}]".format(self.__class__.__name__, self.size, self.height)

    def apply(self, image):
        image = image.copy()
        min_area = self.area.value
        min_height = self.height.value
        mask = self.prepare_invalid_contours(image, min_area, min_height)
        image = cv2.bitwise_and(image, image, mask=mask)
        return image

    def prepare_invalid_contours(self, image, area_size, min_heigth):
        mask = np.ones(image.shape[:2], dtype="uint8") * 255
        contours, hierarchy = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = [contour for contour in contours if ((cv2.contourArea(contour) <= area_size) or (cv2.boundingRect(contour)[3] <= min_heigth))]
        for i in contours:
            cv2.drawContours(mask, [i], -1, 0, -1)
        return mask