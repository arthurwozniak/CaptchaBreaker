class AbstractParserOperation:

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