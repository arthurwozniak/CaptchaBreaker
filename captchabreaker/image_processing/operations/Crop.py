from .AbstractParserOperation import AbstractParserOperation
from captchabreaker.image_processing.operations.parameters.Integer import Integer


class Crop(AbstractParserOperation):
    _custom_name = "Crop"

    def __init__(self):
        super(Crop, self).__init__()
        self.size = Integer(value=2, min=0, max=255, name="size")

    def __str__(self):
        return "[{0}; size: {1}]".format(self.__class__.__name__, self.size)

    def apply(self, image):
        image = image.copy()
        height, width = image.shape[:2]
        crop_size = self.size.value
        cropped = image[crop_size:(height - crop_size), crop_size:(width - crop_size)]  # [y: y + h, x: x + w]
        return cropped
