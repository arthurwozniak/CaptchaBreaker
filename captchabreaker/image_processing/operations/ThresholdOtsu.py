from .AbstractParserOperation import AbstractParserOperation
import cv2


class ThresholdOtsu(AbstractParserOperation):
    _custom_name = "Otsu's treshold"

    def __init__(self):
        super(ThresholdOtsu, self).__init__()

    def apply(self, image):
        image = image.copy()
        tresholded = cv2.threshold(
            image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        return tresholded
