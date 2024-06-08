import torch
from transformers import BertTokenizer, BertForSequenceClassification, AdamW


class BertTextClassifier:
    def __init__(self, num_labels, model_path=None):
        self.tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
        if model_path:
            self.model = BertForSequenceClassification.from_pretrained(model_path)
        else:
            self.model = BertForSequenceClassification.from_pretrained('bert-base-uncased', num_labels=num_labels)
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model.to(self.device)
        self.optimizer = AdamW(self.model.parameters(), lr=2e-5)
        print(f'You are using {self.device}')

    def tokenize_data(self, texts):
        return self.tokenizer(
            texts,
            padding=True,
            truncation=True,
            return_tensors='pt'
        )

    def train(self, train_dataloader, epochs=3):
        self.model.train()
        for epoch in range(epochs):
            total_loss = 0
            for batch in train_dataloader:
                self.optimizer.zero_grad()
                inputs = {key: val.to(self.device) for key, val in batch.items()}
                outputs = self.model(**inputs)
                loss = outputs.loss
                loss.backward()
                self.optimizer.step()
                total_loss += loss.item()
            print(f'Epoch {epoch + 1}, Train Loss: {total_loss / len(train_dataloader)}')

    def evaluate(self, test_dataloader):
        self.model.eval()
        total_correct = 0
        total_samples = 0
        with torch.no_grad():
            for batch in test_dataloader:
                inputs = {key: val.to(self.device) for key, val in batch.items()}
                outputs = self.model(**inputs)
                predictions = torch.argmax(outputs.logits, dim=-1)
                total_correct += (predictions == inputs['labels']).sum().item()
                total_samples += len(inputs['labels'])
        return total_correct / total_samples

    def save(self, save_directory):
        self.model.save_pretrained(save_directory)
        self.tokenizer.save_pretrained(save_directory)

    @classmethod
    def load(cls, load_directory):
        return cls(num_labels=None, model_path=load_directory)  # num_labels is not needed when loading a pretrained model