from typing import Union, List

import numpy as np
import torch
from transformers import BertTokenizer, BertModel


class BertEmbeddings:
    def __init__(self, model_name: str = "bert-base-multilingual-cased", max_length: int = 128, use_compile: bool = True):
        """
        Initialize BERT tokenizer and model.

        :param model_name: Name of the BERT model to use.
        :param max_length: Maximum token length for input text.
        """
        self.model_name = model_name # could also use "bert-base-multilingual-cased" or "bert-base-uncased"
        self.max_length = max_length
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # Load tokenizer and model
        self.tokenizer = BertTokenizer.from_pretrained(self.model_name)
        self.model = BertModel.from_pretrained(self.model_name)
        self.model.to(self.device)
        self.model.eval()  # Set model to evaluation mode

        if use_compile and hasattr(torch, "compile"):
            self.model = torch.compile(self.model)

    def get_bert_embedding(self, text: Union[str, List[str]], pooling: str = "mean") -> np.ndarray:
        """
        Get BERT embeddings for a single string or a list of strings.

        :param text: A single text or a list of texts.
        :param pooling: Pooling strategy for obtaining sentence embeddings.
        :return: NumPy array of embeddings.
        """
        if isinstance(text, str):
            text = [text]  # Convert to list if single string

        # Tokenize and move tensors to device
        encoded_input = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=self.max_length
        ).to(self.device)

        with torch.no_grad():
            output = self.model(**encoded_input)

        if pooling == "mean":
            embedding = output.last_hidden_state.mean(dim=1)  # Average across tokens
        else:
            embedding = output.last_hidden_state[:, 0, :]  # CLS token

        return embedding.squeeze(0).cpu().numpy()  # Convert to NumPy for easier use

    def save_embedding(self, text: str, save_path: str, pooling: str = "mean"):
        """Compute and save BERT embeddings to a file."""
        embedding = self.get_bert_embedding(text, pooling)
        np.save(save_path, embedding)  # Saves as .npy file

    def load_embedding(self, save_path: str) -> np.ndarray:
        """Load a saved BERT embedding from a file."""
        return np.load(save_path)