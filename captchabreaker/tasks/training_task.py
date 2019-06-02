import os

import torch
import torch.nn.functional as F
import torch.optim as optim
from celery import states
from torch.autograd import Variable
from torch.utils.data import DataLoader
from sqlalchemy.orm.attributes import flag_modified

from captchabreaker import celery, app
from captchabreaker.image_processing.classificators import CNN
from captchabreaker.image_processing.classificators.dataset import CaptchaBreakerDataset
from captchabreaker.models import DatasetModel, ClassificatorModel, db


@celery.task(bind=True)
def training_task(self, classificator_id):
    classificator = __load_classificator(self, classificator_id)
    cnn, optimizer, data_loader = __initialize_network(classificator)
    cnn.train()

    losses = []
    last_loss = 0

    for current_iteration in range(classificator.config['iterations']):
        last_loss = __make_step(cnn, data_loader, optimizer)
        losses.append(last_loss)
        __update_task_state(self, states.STARTED, current_iteration, last_loss)

    __update_task_state(self, states.SUCCESS, current_iteration, last_loss)
    __store_result(self, cnn, classificator, losses)


def __load_classificator(task, classificator_id):
    classificator = ClassificatorModel.query.get(classificator_id)
    classificator.task_id = task.request.id
    db.session.commit()
    return classificator


def __initialize_network(classificator):
    dataset = DatasetModel.query.get(classificator.dataset_id)
    batch_size = dataset.characters_per_image
    train_dataset = CaptchaBreakerDataset(dataset)
    data_loader = DataLoader(dataset=train_dataset, batch_size=batch_size, shuffle=True)

    # model of cnn
    cnn = CNN(len(dataset.known_characters))
    # standard gradient decent (defining the learning rate and momentum)
    optimizer = optim.SGD(cnn.parameters(), lr=classificator.config['learning_rate'], momentum=classificator.config['momentum'])

    return cnn, optimizer, data_loader

def __make_step(cnn, data_loader, optimizer):
    for batch_idx, (data, target) in enumerate(data_loader):
        data, target = Variable(data), Variable(target)

        optimizer.zero_grad()  # necessary for new sum of gradients
        output = cnn(data)  # call the forward() function (forward pass of network)
        loss = F.nll_loss(output, target)  # use negative log likelihood to determine loss
        loss.backward()  # backward pass of network (calculate sum of gradients for graph)
        optimizer.step()  # perform model perameter update (update weights)

    return float(loss.item())


def __update_task_state(task, status, iteration, loss):
    task.update_state(state=status,
                 meta={'current_iteration': iteration, 'loss': loss})


def __store_result(task, cnn, classificator, losses):
    torch.save(cnn.state_dict(), os.path.join(app.config['MODEL_DIRECTORY'], task.request.id))
    classificator.is_finished = True
    classificator.config['losses'] = losses
    flag_modified(classificator, 'config')
    db.session.commit()
