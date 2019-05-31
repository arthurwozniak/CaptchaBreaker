import torch.nn as nn
import torch.nn.functional as F


class CNN(nn.Module):
    # https://github.com/rensutheart/PyTorch-Deep-Learning-Tutorials/blob/master/part3_MNIST.py
    def __init__(self, n_classes):
        super(CNN, self).__init__()
        # define all the components that will be used in the NN (these can be reused)
        self.conv1 = nn.Conv2d(1, 10, kernel_size=5, padding=2)  # 1 input feature, 10 output filters
        self.conv2 = nn.Conv2d(10, 20, kernel_size=5, padding=2)  # 10 input filters, 20 output filters
        self.mp = nn.MaxPool2d(2)
        self.drop2D = nn.Dropout2d(p=0.25)
        self.fc1 = nn.Linear(500, 90)
        self.fc2 = nn.Linear(90, n_classes)

    def forward(self, x):
        # define the acutal network
        in_size = x.size(0)  # this is the batch size
        # you can chain function together to form the layers
        x = F.relu(self.mp(self.conv1(x)))
        x = F.relu(self.mp(self.conv2(x)))
        # x = self.drop2D(x)
        x = x.view(in_size, -1)  # flatten data, -1 is inferred from the other dimensions (which is 320 here)
        x = F.relu(self.fc1(x))
        x = self.fc2(x)
        return F.log_softmax(x, dim=1)

    def num_flat_features(self, x):
        size = x.size()[1:]  # all dimensions except the batch dimension
        num_features = 1
        for s in size:
            num_features *= s
        return num_features
