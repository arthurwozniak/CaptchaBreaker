from .Closing import Closing
from .Dilation import Dilation
from .Erosion import Erosion
from .Grayscale import Grayscale
from .Opening import Opening
from .ThresholdCustom import ThresholdCustom
from .ThresholdOtsu import ThresholdOtsu
from captchabreaker.image_processing.operations.parameters.Integer import Integer
from .Inverse import Inverse
from .Crop import Crop

from operator import attrgetter


def operations():
    operations = [Closing(),
                  Dilation(),
                  Erosion(),
                  Opening(),
                  Grayscale(),
                  Inverse(),
                  ThresholdOtsu(),
                  ThresholdCustom(),
                  Crop()]
    return sorted(operations, key=attrgetter('_custom_name'))

def parameters():
    return [Integer()]
