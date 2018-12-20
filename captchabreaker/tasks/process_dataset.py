import random
import time
import pickle
import base64

from captchabreaker import celery, app
from captchabreaker.models import DatasetModel, ClassificatorModel, db

from captchabreaker.image_processing.classificators import CNN
from captchabreaker.image_processing.dataset import CaptchaBreakerDataset

import torch.optim as optim
import torch.nn.functional as F
from torch.autograd import Variable
from torch.utils.data import DataLoader




@celery.task(bind=True)
def long_task(self):
    """Background task that runs a long function with progress reports."""
    verb = ['Starting up', 'Booting', 'Repairing', 'Loading', 'Checking']
    adjective = ['master', 'radiant', 'silent', 'harmonic', 'fast']
    noun = ['solar array', 'particle reshaper', 'cosmic ray', 'orbiter', 'bit']
    message = ''
    total = random.randint(10, 50)
    for i in range(total):
        if not message or random.random() < 0.25:
            message = '{0} {1} {2}...'.format(random.choice(verb),
                                              random.choice(adjective),
                                              random.choice(noun))
        self.update_state(state='PROGRESS',
                          meta={'current': i, 'total': total,
                                'status': message})
        time.sleep(1)
    return {'current': 100, 'total': 100, 'status': 'Task completed!',
            'result': 42}

@celery.task()
def short_task():
    return {'current': 100, 'total': 100, 'status': 'Task completed!',
            'result': 42}


@celery.task(bind=True)
def training_task(self, name, dataset_id, accuracy, iterations, task_id=None):
    print("FFFFFF")
    with app.app_context():
        classificator = ClassificatorModel(name=name, task_id=self.request.id, dataset_id=dataset_id, is_finished=False)
        db.session.add(classificator)
        db.session.commit()

        dataset = DatasetModel.query.get(dataset_id)
        batch_size = dataset.characters_per_image
        assert dataset is not None
        train_dataset = CaptchaBreakerDataset(dataset)
        train_loader = DataLoader(dataset=train_dataset, batch_size=batch_size, shuffle=True)

        current_accuracy = 0
        current_iteration = 0
        # model of cnn
        cnn = CNN(len(dataset.known_characters))
        # standard gradient decent (defining the learning rate and momentum)
        optimizer = optim.SGD(cnn.parameters(), lr=0.01, momentum=0.9)

        cnn.train()
        last_loss=None

        while (current_accuracy < accuracy) and (current_iteration < iterations):
            for batch_idx, (data, target) in enumerate(train_loader):
                data, target = Variable(data), Variable(target)

                optimizer.zero_grad()  # necessary for new sum of gradients
                output = cnn(data)  # call the forward() function (forward pass of network)
                loss = F.nll_loss(output, target)  # use negative log likelihood to determine loss
                loss.backward()  # backward pass of network (calculate sum of gradients for graph)
                optimizer.step()  # perform model perameter update (update weights)

                # print the current status of training

            self.update_state(state='PROGRESS',
                              meta={'current_iteration': current_iteration, 'max_iterations': iterations,
                                    'loss': float(loss.data[0]) })
            last_loss = float(loss.data[0])
            current_iteration += 1

        classificator.network = base64.b64encode(pickle.dumps(cnn.state_dict()))
        classificator.is_finished = True
        #db.session.add(classificator)
        db.session.commit()
        return {'current_iteration': current_iteration, 'max_iterations': iterations,
                'loss': last_loss, 'status': 'COMPLETED'}

