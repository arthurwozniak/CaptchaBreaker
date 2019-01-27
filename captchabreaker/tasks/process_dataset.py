import random
import time
import pickle
import base64

from captchabreaker import celery, app
from captchabreaker.models import DatasetModel, ClassificatorModel, db

from captchabreaker.image_processing.classificators import CNN
from captchabreaker.image_processing.dataset import CaptchaBreakerDataset

import torch
import torch.optim as optim
import torch.nn.functional as F
from torch.autograd import Variable
from torch.utils.data import DataLoader

import os


@celery.task(bind=True)
def training_task(self, classificator_id):
    with app.app_context():
        classificator = ClassificatorModel.query.get(classificator_id)
        classificator.task_id = self.request.id
        db.session.commit()

        dataset = DatasetModel.query.get(classificator.dataset_id)
        batch_size = dataset.characters_per_image
        train_dataset = CaptchaBreakerDataset(dataset)
        train_loader = DataLoader(dataset=train_dataset, batch_size=batch_size, shuffle=True)

        current_accuracy = 0
        current_iteration = 0

        target_accuracy = classificator.config['accuracy']
        target_iterations = classificator.config['iterations']
        # model of cnn
        cnn = CNN(len(dataset.known_characters))
        # standard gradient decent (defining the learning rate and momentum)
        optimizer = optim.SGD(cnn.parameters(), lr=0.01, momentum=0.9)

        cnn.train()
        last_loss = None

        while (current_accuracy < target_accuracy) and (current_iteration < target_iterations):
            for batch_idx, (data, target) in enumerate(train_loader):
                data, target = Variable(data), Variable(target)

                optimizer.zero_grad()  # necessary for new sum of gradients
                output = cnn(data)  # call the forward() function (forward pass of network)
                loss = F.nll_loss(output, target)  # use negative log likelihood to determine loss
                loss.backward()  # backward pass of network (calculate sum of gradients for graph)
                optimizer.step()  # perform model perameter update (update weights)

                # print the current status of training

            self.update_state(state='PROGRESS',
                              meta={'current_iteration': current_iteration, 'max_iterations': target_iterations,
                                    'loss': float(loss.item())})
            last_loss = float(loss.item())
            current_iteration += 1

        torch.save(cnn.state_dict(), os.path.join(app.config['MODEL_DIRECTORY'], self.request.id))
        classificator.is_finished = True
        # db.session.add(classificator)
        db.session.commit()
        return {'current_iteration': current_iteration, 'max_iterations': target_iterations,
                'loss': last_loss, 'status': 'COMPLETED'}
