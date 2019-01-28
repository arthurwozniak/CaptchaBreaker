import json
import os
import re

import numpy as np
import torch
from torch.autograd.variable import Variable

from captchabreaker.config import MODEL_DIRECTORY
from captchabreaker.image_processing.classificators.cnn import CNN
from captchabreaker.image_processing.dataset_extractor import DatasetExtractor
from captchabreaker.image_processing.helper import parse_operations
from captchabreaker.models import DatasetModel


class CaptchaDecoder:

    def __init__(self, image, classificator):
        self.image = image
        self.classificator = classificator
        if self.classificator is None:
            raise Exception("Unknown classificator")
        self.dataset = DatasetModel.query.get(self.classificator.dataset_id)

    def result(self):
        return self.recognize_characters(self.extract_characters())

    def extract_characters(self):
        operations = parse_operations(json.loads(re.sub("'", '"', self.dataset.extraction_config)))
        datasetExtractor = DatasetExtractor(None, operations, None, self.dataset.characters_per_image, None)
        return datasetExtractor.process_file(self.image)

    def recognize_characters(self, characters):
        cnn = CNN(len(self.dataset.known_characters))
        path = os.path.join(MODEL_DIRECTORY, self.classificator.task_id)
        cnn.load_state_dict(torch.load(path))
        characters = np.array(characters)
        characters = torch.from_numpy((characters.astype(dtype=np.float32) / 255).reshape([5, 1, 20, 20]))
        data = Variable(characters)
        cnn.eval()
        output = cnn(data)
        pred = output.data.max(1, keepdim=True)[1]
        data = pred.squeeze().tolist()
        dataset_characters = self.dataset.known_characters
        return "".join(map(lambda x: dataset_characters[x], data))
