import pandas as pd
import torch
from sklearn.model_selection import train_test_split
from torch.utils.data import Dataset, DataLoader

from ai.bert_embedding_model import BertEmbeddings
from program.constants import SECRETS_DIR, Tags


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

class MultimodalDataset(Dataset):
    def __init__(self, dataframe: pd.DataFrame, numeric_cols: list, text_cols: list, label_col: str):
        """
        Custom PyTorch Dataset for multimodal data.

        :param dataframe: Pandas DataFrame containing the dataset
        :param numeric_cols: List of column names for numeric features
        :param text_cols: List of column names for text embeddings (precomputed)
        :param label_col: Column name for the target labels
        """
        self.numeric_data = torch.tensor(dataframe[numeric_cols].values, dtype=torch.float32)
        self.text_data = torch.tensor(dataframe[text_cols].values, dtype=torch.float32)
        self.labels = torch.tensor(dataframe[label_col].values, dtype=torch.long)  # Use long for classification

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        return self.numeric_data[idx], self.text_data[idx], self.labels[idx]


def load_data(file_path, is_rebuild_bert_embds: bool =False):
    """Load CSV data and extract year, month, and, day from the date column."""
    data = pd.read_csv(file_path, usecols=['date', 'description', 'amount_usd', 'tag'])

    return preprocess_historical_data(data, is_rebuild_bert_embds)


def preprocess_historical_data(data, is_rebuild_bert_embds: bool = False):
    """Preprocess data by extracting year, month, and day from the date column. Also, fill NaN values in the description column with empty strings."""
    print("Preprocessing data...")
    data['date'] = pd.to_datetime(data['date'])
    data[['year', 'month', 'day']] = data['date'].apply(lambda x: pd.Series([x.year, x.month, x.day, ]))
    data['description'] = data['description'].fillna('')
    try:
        data['label'] = data['tag'].map(lambda x: Tags[x].value)
    except KeyError:
        print("No tag column found. Skipping label assignment.")
    embedder = BertEmbeddings()
    if is_rebuild_bert_embds:
        embeddings = embedder.get_bert_embedding(data['description'].tolist(), pooling='cls')
        embedder.save_embedding(data['description'].tolist(), f"{SECRETS_DIR}/private/saved_model/embeddings.npy", pooling='cls')
    else:
        embeddings = embedder.load_embedding(
            f"{SECRETS_DIR}/private/saved_model/embeddings.npy")
    data.drop(columns=['tag', 'date'], inplace=True)
    print("Data preprocessing complete.")
    return pd.concat([data, pd.DataFrame(embeddings)], axis=1)

def preprocess_data_old(data, is_prediction_data=False):
    labels, label_to_id = None, None
    if not is_prediction_data:
        label_to_id = {label: idx for idx, label in enumerate(data['tag'].unique())}
        labels = [label_to_id[label] for label in data['tag']]
    descriptions = data['description'].tolist()
    # replace NaN values with empty strings
    descriptions = [desc if type(desc) == str else '' for desc in descriptions]
    amounts = data['amount_usd'].tolist()
    features = [f'{amount} {desc}' for desc, amount in zip(descriptions, amounts)]
    return features, labels, label_to_id


def split_data(X, y, test_size=0.2):
    train_X, test_X, train_y, test_y = train_test_split(X, y, test_size=test_size, random_state=42)
    return train_X, test_X, train_y, test_y


def create_dataloaders(train_X, train_y, test_X=None, test_y=None, tokenizer=None, batch_size=16):
    train_tokens = tokenizer(train_X)
    train_dataset = BudgetDataset(train_tokens, train_y)
    train_dataloader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)

    if test_X is not None or test_y is not None:
        test_tokens = tokenizer(test_X)
        test_dataset = BudgetDataset(test_tokens, test_y)
        test_dataloader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)
    else:
        test_dataloader = None

    return train_dataloader, test_dataloader



def create_dataloader(dataframe: pd.DataFrame, numeric_cols: list, text_cols: list, label_col: str, batch_size=32, shuffle=True):
    """
    Creates a PyTorch DataLoader from a DataFrame.

    :param dataframe: Pandas DataFrame containing the dataset
    :param numeric_cols: List of numeric feature column names
    :param text_cols: List of text feature column names (embeddings)
    :param label_col: Name of the column containing labels
    :param batch_size: Batch size for DataLoader
    :param shuffle: Whether to shuffle the data
    :return: PyTorch DataLoader
    """
    dataset = MultimodalDataset(dataframe, numeric_cols, text_cols, label_col)
    return DataLoader(dataset, batch_size=batch_size, shuffle=shuffle)
