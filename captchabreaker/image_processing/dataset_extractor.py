import base64
import io
import zipfile
from os.path import basename

from captchabreaker import modifier
from captchabreaker.models import DatasetModel, CharacterModel, OriginalImageModel


class DatasetExtractor:

    def __init__(self, file, operations, name, count, operations_json, labels=None):
        self.file = file
        self.operations = operations
        self.labels = labels
        self.count = count
        if file is not None:
            buf = io.BytesIO(base64.b64decode(self.file))
            self.zip = zipfile.ZipFile(buf)
        self.name = name
        self.operations_json = operations_json

    def process_zip(self):
        items = self.zip.infolist()
        archive_data = []

        for i, item in enumerate(items):
            if item.is_dir():
                continue
            name = self.labels[item.filename] if self.labels else basename(item.filename).split(".")[0]
            if len(name) != self.count:
                raise Exception(
                    "Length of label `{0}` ({1}) does not match count of characters in CAPTCHA ({2}).".format(name,
                                                                                                              len(name),
                                                                                                              self.count))
            image_data = {}
            char_dict = []
            image_data["name"] = name
            raw_image = self.zip.read(item)
            image_data["image"] = base64.b64encode(raw_image).decode()
            characters = self.process_file(modifier.bin_to_img(raw_image))
            if self.count != len(characters): continue
            for character_data, character_str in zip(characters, name):
                char_dict.append((character_str, character_data))
            image_data["characters"] = char_dict
            archive_data.append(image_data)
        return archive_data

    def process_file(self, image):
        last_img = image
        images = [last_img]
        for op in self.operations:
            images.append(op.apply(images[-1]))
        boxes = modifier.find_boxes(images[-1], self.count)
        return modifier.get_letters(images[-1], boxes)

    def perform(self):
        from captchabreaker.models import db
        import cv2

        dataset = DatasetModel(name=self.name)
        dataset.characters_per_image = self.count

        known = set()

        archive_data = self.process_zip()

        for captcha in archive_data:
            image = OriginalImageModel(text=captcha["name"], data=captcha["image"], dataset=dataset)
            known.update(set(list(captcha["name"])))
            for character_tuple in captcha["characters"]:
                character_image = cv2.imencode('.bmp', character_tuple[1])[1].tostring()
                character_image = base64.b64encode(character_image).decode()
                character = CharacterModel(character=character_tuple[0], data=character_tuple[1], original=image,
                                           image=character_image)
                image.characters.append(character)
            dataset.original_images.append(image)
        dataset.known_characters = "".join(sorted(list(known)))
        dataset.config = self.operations_json
        db.session.add(dataset)
        db.session.commit()

        return dataset
