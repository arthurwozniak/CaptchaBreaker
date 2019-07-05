from functools import reduce

import torch
import torch.nn.functional as F
from torch import optim
from torch.autograd import Variable
from torch.utils.data import random_split, DataLoader

from captchabreaker import CNN
from captchabreaker.image_processing.classificators.dataset import CaptchaBreakerDataset
from captchabreaker.models import ClassificatorModel, DatasetModel


class Verificator:

    def __init__(self, classificator_id, print_progress=False):
        self.classificator = ClassificatorModel.query.get(classificator_id)
        self.dataset = DatasetModel.query.get(self.classificator.dataset_id)
        self.batch_size = self.dataset.characters_per_image
        self.torch_dataset = CaptchaBreakerDataset(self.dataset)
        self.n_fold = self.classificator.config['cross_validation']
        self.results = []
        self.dataset_splits = self.prepare_splits()
        self.print_progress = print_progress

    def perform(self):
        for iteration in range(self.n_fold):
            if self.print_progress:
                print("Performing %i iteration" % iteration)
            self.perform_validation(iteration)

        return self.results

    def prepare_splits(self):
        split_size = len(self.torch_dataset) // self.n_fold
        splits = [split_size] * self.n_fold
        splits[-1] += len(self.torch_dataset) - sum(splits)
        return random_split(self.torch_dataset, splits)

    def perform_validation(self, iteration):
        train_loader, test_loader = self.create_data_loaders(iteration)
        cnn = CNN(len(self.dataset.known_characters))

        self.train_network(cnn, train_loader)
        accuracy = self.validate_network(cnn, test_loader)
        self.results.append({'iteration': iteration, 'accuracy': accuracy})

    def create_data_loaders(self, iteration):
        trains_indexes = list(filter(lambda x: x != iteration, range(self.n_fold)))
        trains_subsets = map(lambda index: self.dataset_splits[index], trains_indexes)
        train_set = list(reduce(lambda x, y: x + y, trains_subsets))
        test_set = self.dataset_splits[iteration]
        train_loader = DataLoader(dataset=train_set, batch_size=self.batch_size)
        test_loader = DataLoader(dataset=test_set, batch_size=self.batch_size)
        return (train_loader, test_loader)

    def train_network(self, cnn, data_loader):
        optimizer = optim.SGD(cnn.parameters(), lr=self.classificator.config['learning_rate'],
                              momentum=self.classificator.config['momentum'])
        for current_iteration in range(self.classificator.config['iterations']):
            if self.print_progress:
                print("current iteration: ", current_iteration)
            for batch_idx, (data, target) in enumerate(data_loader):
                data, target = Variable(data), Variable(target)

                optimizer.zero_grad()  # necessary for new sum of gradients
                output = cnn(data)  # call the forward() function (forward pass of network)
                loss = F.nll_loss(output, target)  # use negative log likelihood to determine loss
                loss.backward()  # backward pass of network (calculate sum of gradients for graph)
                optimizer.step()  # perform model perameter update (update weights)

    def validate_network(self, cnn, data_loader):
        correct = 0
        total = 0
        with torch.no_grad():
            for data in data_loader:
                images, labels = data
                outputs = cnn(images)
                _, predicted = torch.max(outputs.data, 1)
                total += labels.size(0)
                correct += (predicted == labels).sum().item()
        return correct / total
