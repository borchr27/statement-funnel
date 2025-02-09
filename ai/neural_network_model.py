# Try a torch Neural Network
import os
from typing import Tuple, Optional

import pandas as pd
import torch
from torch import optim, nn
from torch.utils.data import TensorDataset, DataLoader

from program.constants import N_CLASSES, N_NUMERICAL_FEATURES

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from typing import Tuple

class MultimodalModel(nn.Module):
    def __init__(self, numeric_input_dim=N_NUMERICAL_FEATURES, text_input_dim=768, hidden_dim=128, output_dim=N_CLASSES):
        super().__init__()

        self.numeric_branch = nn.Sequential(
            nn.Linear(numeric_input_dim, 64),
            nn.ReLU(),
            nn.Dropout(0.1),
        )

        self.text_branch = nn.Sequential(
            nn.Linear(text_input_dim, 256),
            nn.ReLU(),
            nn.Dropout(0.1),
        )

        self.fusion = nn.Sequential(
            nn.Linear(64 + 256, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(hidden_dim, output_dim)
        )

    def forward(self, numeric_x, text_x):
        numeric_out = self.numeric_branch(numeric_x)
        text_out = self.text_branch(text_x)
        fused = torch.cat([numeric_out, text_out], dim=1)
        return self.fusion(fused)


    # def predict(self, numeric_x: torch.Tensor, text_x: torch.Tensor) -> torch.Tensor:
    #     """
    #     Perform a forward pass and return the predicted class.
    #
    #     :param numeric_x: Tensor of numeric features (batch_size, numeric_input_dim)
    #     :param text_x: Tensor of text features (batch_size, text_input_dim)
    #     :return: Tensor of predicted classes (batch_size,)
    #     """
    #     self.eval()  # Set to evaluation mode
    #     with torch.no_grad():
    #         outputs = self.forward(numeric_x, text_x)  # Forward pass
    #         predictions = torch.argmax(outputs, dim=1)  # Get class with highest probability
    #     return predictions


class MultimodalTrainer:
    def __init__(self, model: nn.Module, lr=1e-3, num_epochs=30, train_loader: Optional[DataLoader] = None, test_loader: Optional[DataLoader] = None):
        """
        Wrapper class for training & evaluating the multimodal model.

        :param model: The multimodal model to train.
        :param train_loader: DataLoader for training data.
        :param test_loader: DataLoader for testing data.
        :param lr: Learning rate.
        :param num_epochs: Number of training epochs.
        """
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = model.to(self.device)
        self.criterion = nn.CrossEntropyLoss()
        self.optimizer = optim.AdamW(self.model.parameters(), lr=lr)
        self.num_epochs = num_epochs
        self.train_loader = train_loader
        self.test_loader = test_loader

    def train(self):
        """ Train the model """
        print("Training the model...")
        self.model.train()
        for epoch in range(self.num_epochs):
            total_loss = 0.0
            for batch_numeric, batch_text, batch_labels in self.train_loader:
                batch_numeric, batch_text, batch_labels = batch_numeric.to(self.device), batch_text.to(self.device), batch_labels.to(self.device)

                self.optimizer.zero_grad()
                outputs = self.model(batch_numeric, batch_text)
                loss = self.criterion(outputs, batch_labels)
                loss.backward()
                self.optimizer.step()
                total_loss += loss.item()

            avg_loss = total_loss / len(self.train_loader)
            print(f"Epoch [{epoch + 1}/{self.num_epochs}], Loss: {avg_loss:.4f}")

    def evaluate(self) -> Tuple[float, float]:
        """ Evaluate the model on the test set """
        print("Evaluating the model...")
        self.model.eval()
        correct, total, total_loss = 0, 0, 0.0

        with torch.no_grad():
            for batch_numeric, batch_text, batch_labels in self.test_loader:
                batch_numeric, batch_text, batch_labels = batch_numeric.to(self.device), batch_text.to(self.device), batch_labels.to(self.device)

                outputs = self.model(batch_numeric, batch_text)
                loss = self.criterion(outputs, batch_labels)
                total_loss += loss.item()

                predictions = torch.argmax(outputs, dim=1)
                correct += (predictions == batch_labels).sum().item()
                total += batch_labels.size(0)

        accuracy = correct / total
        avg_loss = total_loss / len(self.test_loader)
        print(f"Test Accuracy: {accuracy:.3f}, Test Loss: {avg_loss:.4f}")
        return accuracy, avg_loss

    def predict(self, numeric_x, text_x) -> torch.Tensor:
        """
        Predict classes for new input data.

        :param numeric_x: Pandas DataFrame or PyTorch Tensor of numeric features
        :param text_x: Pandas DataFrame or PyTorch Tensor of text features
        :return: Predicted class labels
        """
        # Convert DataFrames to PyTorch tensors if needed
        if isinstance(numeric_x, pd.DataFrame):
            numeric_x = torch.tensor(numeric_x.values, dtype=torch.float32)
        if isinstance(text_x, pd.DataFrame):
            text_x = torch.tensor(text_x.values, dtype=torch.float32)

        numeric_x, text_x = numeric_x.to(self.device), text_x.to(self.device)

        self.model.eval()
        with torch.no_grad():
            outputs = self.model(numeric_x, text_x)
            predictions = torch.argmax(outputs, dim=1)

        return predictions

    def save(self, save_directory: str):
        """Save model and optimizer state safely."""
        print(f"Saving model to {save_directory}")
        os.makedirs(os.path.dirname(save_directory), exist_ok=True)  # Ensure parent directory exists

        checkpoint = {
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'num_epochs': self.num_epochs
        }

        torch.save(checkpoint, save_directory)
        print(f"Model saved to {save_directory}")

    @classmethod
    def load(cls, model_class: nn.Module, model_path: str, lr=1e-3):
        """
        Load a trained model and optimizer state.

        :param model_class: Class of the multimodal model to instantiate.
        :param model_path: Path to the saved model file.
        :param lr: Learning rate for continued training.
        :return: Loaded MultimodalTrainer instance.
        """
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # Instantiate model
        model = model_class()
        model.to(device)

        # Load checkpoint
        checkpoint = torch.load(model_path, map_location=device)
        model.load_state_dict(checkpoint['model_state_dict'])

        # Initialize Trainer instance
        trainer = cls(model, lr, num_epochs=checkpoint['num_epochs'])

        # Load optimizer state
        trainer.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])

        print(f"Model loaded from {model_path}")
        return trainer