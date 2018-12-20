import torch
import numpy as np
from torch.utils.data import Dataset


class CaptchaBreakerDataset(Dataset):

    def __init__(self, db_model):
        self.dataset_model = db_model
        self.size = (self.dataset_model.characters_per_image * len(self.dataset_model.original_images))
        self.characters = self.dataset_model.known_characters

    def __len__(self):
        return self.size

    def __getitem__(self, item):
        image_number = item // self.dataset_model.characters_per_image
        character_number = item % self.dataset_model.characters_per_image
        character = self.dataset_model.original_images[image_number].characters[character_number]
        return (torch.from_numpy(
            (np.fromstring(character.data, dtype=np.uint8).astype(dtype=np.float32) / 255).reshape([1, 20, 20])),
                self.characters.index(str(character.character)))
