"""Class creating and training the ANN model from time series data"""

import pandas as pd
import numpy as np

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.utils.data as D

from data_transformation import min_max_scaler, split
from tensor import Tensor

# Import data

data = pd.read_csv("data/training_data.csv")
data = data.drop("Date", axis=1)

# Split and normalize data

training_data, testing_data = split(data, 0.75)
training_data = min_max_scaler(training_data)
testing_data = min_max_scaler(testing_data)

testing_target = testing_data["GLD Price"]
testing_features = testing_data.drop("GLD Price", axis=1)

training_target = training_data["GLD Price"]
training_features = training_data.drop("GLD Price", axis=1) 
    
# Convert DataFrames into Pytorch tensors, along with their respective Pytorch DataLoaders

batch_size = 64

train_tensor = Tensor(features=training_features, target=training_target)
train_dataloader = D.DataLoader(dataset=train_tensor, batch_size=batch_size, shuffle=False)

test_tensor = Tensor(features=testing_features, target=testing_target)
test_dataloader = D.DataLoader(dataset=test_tensor, batch_size=batch_size, shuffle=False)

# Creating our prediction ANN

class GLDPredictor(nn.Module):
    """
    Artificial Neural Network predicting the price of $GLD. 
    Three layers of neruons, using affine linear transformations and ReLU activation functions.
    """

    def __init__(self):
        super(GLDPredictor, self).__init__()
        self.layer1 = nn.Linear(in_features=9, out_features=12, dtype=torch.float64)
        self.layer2 = nn.Linear(in_features=12, out_features=12, dtype=torch.float64)
        self.output = nn.Linear(in_features=12, out_features=1, dtype=torch.float64)

    def forward(self, x):
        x = F.relu(self.layer1(x))
        x = F.relu(self.layer2(x))
        x = F.relu(self.output(x))

        return x
    
# Training GLDPredictor on our training data

model = GLDPredictor()

# Instantiate our loss function

learning_rate = 0.1
loss_function = nn.L1Loss() # Mean absoloute error
optimizer = torch.optim.Adam(model.parameters(), learning_rate)

# Our training loop

epochs = 100
loss_values = []

for epoch in range(epochs):
    for features, target in train_dataloader:
        optimizer.zero_grad()

        # Forward pass
        prediction = model(features)
        loss = loss_function(prediction, target.unsqueeze(-1))
        loss_values.append(loss.item())

        # Backward pass + optimization
        loss.backward()
        optimizer.step()

        # Print out loss
        if epoch % 10 == 0:
            print(loss.item())

print(f"Training Complete. Final loss: {loss_values[-1]}")

# Save our trained model

torch.save(model.state_dict(), "models/GLDtrained1.plt")