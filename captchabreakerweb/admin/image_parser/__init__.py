import inspect
import sys

from .Closing import Closing
from .Dilation import Dilation
from .Erosion import Erosion
from .Grayscale import Grayscale
from .Opening import Opening
from .TresholdCustom import TresholdCustom
from .TresholdOtsu import TresholdOtsu


def get_operations():
    operations = []
    for name, obj in inspect.getmembers(sys.modules[__name__]):
        if inspect.isclass(obj):
            operations.append(obj())
    return sorted(operations, key=lambda op: op.name)
