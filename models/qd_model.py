import torch
import torch.nn as nn
import torch.nn.functional as F
from config import params

"""
Architecture based on InfoGAN paper.
"""
#Placeholder for now
num_z = params['num_z']
#self.num_dis_c = 1
dis_c_dim = params['dis_c_dim']
num_con_c = params['num_con_c']
class Generator(nn.Module):


    def __init__(self):
        super().__init__()

        #self.tconv1 = nn.ConvTranspose2d(74, 1024, 1, 1, bias=False)
        self.fc1 = nn.Linear(num_z+dis_c_dim+num_con_c, 1024)
        self.bn1 = nn.BatchNorm1d(1024)

        #self.tconv2 = nn.ConvTranspose2d(1024, 128, 7, 1, bias=False)
        self.fc2 = nn.Linear(1024, 256*7*7)
        self.bn2 = nn.BatchNorm2d(256)

        self.tconv0 = nn.ConvTranspose2d(256, 128, 4, 2, padding=1, bias=True)
        self.bn0 = nn.BatchNorm2d(128)

        self.tconv1 = nn.ConvTranspose2d(128, 64, 4, 2, padding=1, bias=True)
        self.bn3 = nn.BatchNorm2d(64)

        self.tconv2 = nn.Conv2d(64, 1, 1, 1, 0, bias=True)

    def forward(self, x):
        x = x.view(-1, num_z+dis_c_dim+num_con_c)
        x = F.relu(self.bn1(self.fc1(x)))
        #print(x.shape)
        x = self.fc2(x)
        x = x.view(-1, 256, 7, 7)
        x = F.relu(self.bn2(x))
        #x = F.relu(self.bn2(self.fc2))
        #print(x.shape)
        x = F.relu(self.bn0(self.tconv0(x)))
        #print(x.shape)
        x = self.tconv1(x)
        x = self.bn3(x)
        x = F.relu(x)
        #x = F.relu(self.bn3(self.tconv1(x)))
        #print(x.shape)
        img = torch.tanh(self.tconv2(x))
        #print(img.shape)


        return img

class Discriminator(nn.Module):
    def __init__(self):
        super().__init__()

        self.conv1 = nn.Conv2d(1, 64, 4, 2, 1)

        self.conv2 = nn.Conv2d(64, 128, 4, 2, 1, bias=False)
        self.bn2 = nn.BatchNorm2d(128)

        #self.conv3 = nn.Conv2d(128, 1024, 7, bias=False)
        self.fc1 = nn.Linear(128*7*7, 1024)
        self.bn3 = nn.BatchNorm1d(1024)

    def forward(self, x):
        x = F.leaky_relu(self.conv1(x), 0.1, inplace=True)
        x = F.leaky_relu(self.bn2(self.conv2(x)), 0.1, inplace=True)
        x = x.view(-1, 128*7*7)
        x = F.leaky_relu(self.bn3(self.fc1(x)), 0.1, inplace=True)

        return x

class DHead(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv = nn.Linear(1024, 1)

    def forward(self, x):
        output = torch.sigmoid(self.conv(x))
        return output

class QHead(nn.Module):
    def __init__(self):
        super().__init__()

        #self.conv1 = nn.Conv2d(1024, 128, 1, bias=False)
        self.fc1 = nn.Linear(1024, 128)
        self.bn1 = nn.BatchNorm1d(128)

        """
        self.conv_disc = nn.Conv2d(128, 10, 1)
        self.conv_mu = nn.Conv2d(128, 2, 1)
        self.conv_var = nn.Conv2d(128, 2, 1)
        """
        self.conv_disc = nn.Linear(128, dis_c_dim)
        self.conv_mu = nn.Linear(128, num_con_c)
        self.conv_var = nn.Linear(128, num_con_c)

    def forward(self, x):
        x = x.view(-1, 1024)
        x = F.leaky_relu(self.bn1(self.fc1(x)), 0.1, inplace=True)

        disc_logits = self.conv_disc(x).squeeze()

        mu = self.conv_mu(x).squeeze()
        var = torch.exp(self.conv_var(x).squeeze())

        return disc_logits, mu, var