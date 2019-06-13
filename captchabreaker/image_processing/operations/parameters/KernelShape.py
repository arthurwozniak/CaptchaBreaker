import uuid
from cv2 import MORPH_RECT, MORPH_CROSS, MORPH_ELLIPSE


class KernelShape:

    TYPES = {'MORPH_RECT': MORPH_RECT,
             'MORPH_CROSS': MORPH_CROSS,
             'MORPH_ELLIPSE': MORPH_ELLIPSE}


    _html_pattern = """<div class="col-md-6"><label for="{1}">{2}</label></div> 
    <div class="col-md-6"><select class="form-control" id="{1}" data-class="{0}" data-name="{2}" data-type="type" onChange="fileSelectChanged()">
    <option value="MORPH_RECT">square</option>
    <option value="MORPH_ELLIPSE">circle</option>
    <option value="MORPH_CROSS">cross</option>    
    </select></div>"""


    def __init__(self, name="variable", type="MORPH_RECT"):
        self.type = type
        self.name = name
        self.id = uuid.uuid4().hex

    def __int__(self):
        return self.value

    def html(self):
        html = self._html_pattern.format(self.__class__.__name__ , self.id, self.name)
        return html

    def __str__(self):
        return "[{0}; value: {1}]".format(self.__class__.__name__, self.type)

    def __repr__(self):
        return self.__str__()

    def get_type(self):
        return self.TYPES.get(self.type, self.TYPES['MORPH_RECT'])
