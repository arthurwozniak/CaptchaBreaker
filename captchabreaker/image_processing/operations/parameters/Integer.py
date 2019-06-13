import uuid


class Integer:

    _html_pattern = \
    """<div class="col-md-6"><label for="{4}">{5}</label></div> 
    <div class="col-md-6"><input class="form-control" type="number" id="{4}" data-class="{0}" data-name="{5}" data-type="value" min="{1}" max="{2}" value="{3}" onChange="fileSelectChanged()"></div>"""


    def __init__(self, value=0, min=0, max=255, name="variable"):
        self.value = value
        self.min = min
        self.max = max
        self.name = name
        self.id = uuid.uuid4().hex

    def __int__(self):
        return self.value

    def html(self):
        html = self._html_pattern.format(self.__class__.__name__ ,self.min, self.max, self.value, self.id, self.name)
        return html


    def __str__(self):
        return "[{0}; value: {1}]".format(self.__class__.__name__, self.value)

    def __repr__(self):
        return self.__str__()