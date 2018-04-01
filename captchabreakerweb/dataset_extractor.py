import zipfile
import io
import base64
import collections
from captchabreakerweb import modifier
from captchabreakerweb.admin.image_parser import parse_operations
from captchabreakerweb.models import DatasetModel, CharacterModel, OriginalImageModel
from os.path import basename


class DatasetExtractor:

    def __init__(self, file, operations, name, count, operations_json, labels=None):
        self.file = file
        self.operations = operations
        self.labels = labels
        self.count = count
        buf = io.BytesIO(base64.b64decode(self.file))
        self.zip = zipfile.ZipFile(buf)
        self.name = name
        self.operations_json = operations_json


    def process_zip(self):
        items = self.zip.infolist()
        archive_data = []

        print(items)
        for item in items:
            if item.is_dir():
                continue
            name = self.labels[item.filename] if self.labels else basename(item.filename).split(".")[0]
            if len(name) != self.count:
                print("Invalid name length")
                raise Exception("Length of label `{0}` ({1}) does not match count of characters in CAPTCHA ({2}).".format(name, len(name), self.count))
            print(name)
            image_data = {}
            char_dict = []
            image_data["name"] = name
            raw_image = self.zip.read(item)
            image_data["image"] = base64.b64encode(raw_image).decode()
            characters = self.process_file(raw_image)
            for character_data, character_str in zip(characters, name):
                char_dict.append((character_str, character_data))
            image_data["characters"] = char_dict
            archive_data.append(image_data)
        return archive_data

    def process_file(self, image):
        last_img = modifier.bin_to_img(image)
        images = [last_img]
        for op in self.operations:
            images.append(op.apply(images[-1]))
        result = modifier.img_unmask(images[-1], self.count, onlyLetters=True)
        return result


    def process_and_save(self):
        from captchabreakerweb.models import db
        import cv2

        dataset = DatasetModel(name=self.name)
        dataset.characters_per_image = self.count

        known = set()

        archive_data = self.process_zip()

        for captcha in archive_data:
            image = OriginalImageModel(text=captcha["name"], data=captcha["image"], dataset=dataset)
            known.update(set(list(captcha["name"])))
            for character_tuple in captcha["characters"]:
                #print("tuple ", character_tuple)
                character_image = cv2.imencode('.bmp', character_tuple[1])[1].tostring()
                character_image = base64.b64encode(character_image).decode()
                character = CharacterModel(character=character_tuple[0], data=character_tuple[1], original=image, image=character_image)
                image.characters.append(character)
            dataset.original_images.append(image)
        dataset.known_characters = "".join(sorted(list(known)))
        dataset.extraction_config = str(self.operations_json)
        db.session.add(dataset)
        db.session.commit()

        return dataset