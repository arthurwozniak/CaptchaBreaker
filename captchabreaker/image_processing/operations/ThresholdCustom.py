from .AbstractParserOperation import AbstractParserOperation
from captchabreaker.image_processing.operations.parameters.Integer import Integer
import cv2
import numpy as np

class ThresholdCustom(AbstractParserOperation):

    _custom_name = "Custom treshold"
    
    def __init__(self):
        super(ThresholdCustom, self).__init__()
        self.lower_bound = Integer(value=100, min=0, max=255, name="lower_bound")
        self.upper_bound = Integer(value=200, min=0, max=255, name="upper_bound")

    def __str__(self):
        return "[{0}; lower_bound: {1}; upper_bound: {2}]".format(self.__class__.__name__, self.lower_bound, self.upper_bound)

    def apply(self, image):
        image = image.copy()
        tresholded = cv2.inRange(image, np.array([int(self.lower_bound)]), np.array([int(self.upper_bound)]))
        return tresholded