class AbstractParserOperation(object):
    _custom_name = "Here place operation name"

    @property
    def name(self):
        return self._custom_name

    @property
    def desc(self):
        return "Description " + self._custom_name

    def __init__(self):
        return

    def apply(self, image):
        return

    def arg_html(self):
        return "\n".join([self.__getattribute__(attr).html() for attr in self.__dict__])

    def __str__(self):
        return "[{0}]".format(self.__class__.__name__)

    def __repr__(self):
        return self.__str__()
