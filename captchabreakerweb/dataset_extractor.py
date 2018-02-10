import zipfile
import io
import base64
import collections
from captchabreakerweb import modifier


class DatasetExtractor:

    def __init__(self, file, operations, name, labels=None):
        self.file = file
        self.operations = operations
        self.name = name
        self.labels = labels
        buf = io.BytesIO(base64.b64decode(self.file))
        self.zip = zipfile.ZipFile(buf)

    def process_zip(self):
        items = self.zip.infolist()
        char_dict = collections.defaultdict(list)
        print(items)
        for item in items:
            if item.is_dir():
                continue
            name = self.labels[item.filename] if self.labels else item.filename.split(".")[0]
            if len(name) != self.operations["unmask"]["count"]:
                print("Invalid name length")
                continue
            print(name)
            characters = self.process_file(self.zip.read(item))
            for i in range(len(characters)):
                char_dict[name[i]].append(characters[i])
        return char_dict


    def process_file(self, image):
        last_img = modifier.bin_to_img(image)
        if "grayscale" in self.operations.keys():
            last_img = modifier.img_grayscale(last_img)

        if "filter" in self.operations.keys():
            last_img = modifier.img_filter(last_img, self.operations["filter"]["lower"], self.operations["filter"]["upper"])

        if "treshold" in self.operations.keys():
            last_img = modifier.img_treshhold(last_img)

        if "unmask" in self.operations.keys():
            last_img, letters = modifier.img_unmask(last_img, self.operations["unmask"]["count"])
        return letters


    def process_and_save(self, db):
        return None
