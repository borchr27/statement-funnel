import pandas as pd
from sklearn.model_selection import train_test_split
from torch.utils.data import Dataset, DataLoader
import torch


class BudgetDataset(Dataset):
    def __init__(self, tokens, labels):
        self.tokens = tokens
        self.labels = labels

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        item = {key: val[idx] for key, val in self.tokens.items()}
        item['labels'] = torch.tensor(self.labels[idx])
        return item


def load_data(file_path):
    data = pd.read_csv(file_path)
    return data[['Description', 'Amount', 'Tag']]


def preprocess_data(data):
    label_to_id = {label: idx for idx, label in enumerate(data['Tag'].unique())}
    labels = [label_to_id[label] for label in data['Tag']]
    descriptions = data['Description'].tolist()
    # replace NaN values with empty strings
    descriptions = [desc if type(desc) == str else '' for desc in descriptions]
    amounts = data['Amount'].tolist()
    features = [f'{amount} {desc}' for desc, amount in zip(descriptions, amounts)]
    return features, labels, label_to_id


def split_data(texts, labels, test_size=0.4):
    train_texts, test_texts, train_labels, test_labels = train_test_split(texts, labels, test_size=test_size, random_state=42)
    return train_texts, test_texts, train_labels, test_labels


def create_dataloaders(train_features, train_labels, test_features=None, test_labels=None, tokenizer=None, batch_size=16):
    train_tokens = tokenizer(train_features)
    train_dataset = BudgetDataset(train_tokens, train_labels)
    train_dataloader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)

    if test_features is not None or test_labels is not None:
        test_tokens = tokenizer(test_features)
        test_dataset = BudgetDataset(test_tokens, test_labels)
        test_dataloader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)
    else:
        test_dataloader = None

    return train_dataloader, test_dataloader
