from .Closing import Closing
from .Dilation import Dilation
from .Erosion import Erosion
from .Grayscale import Grayscale
from .Opening import Opening
from .ThresholdCustom import ThresholdCustom
from .ThresholdOtsu import ThresholdOtsu
from captchabreaker.image_processing.operations.parameters import Integer, KernelShape
from .Inverse import Inverse
from .Crop import Crop
from .AreaFilter import AreaFilter

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
                  Crop(),
                  AreaFilter()]
    return sorted(operations, key=attrgetter('_custom_name'))

def parameters():
    return [Integer(), KernelShape()]
