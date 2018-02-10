from .AbstractParserOperation import AbstractParserOperation


class TresholdOtsu(AbstractParserOperation):

    _custom_name = "Otsu's treshold"
    
    def __init__(self):
        super(TresholdOtsu, self).__init__()