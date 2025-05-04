import argparse
import os

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import torch
from sklearn.metrics import confusion_matrix


os.environ["ENV"] = ".env.json"

from ai.neural_network_model import MultimodalModel, MultimodalTrainer
from ai.data_loader import load_data, split_data, create_dataloader
from program.constants import Tags, MODEL_SAVE_DIRECTORY, NUMERIC_COLUMNS, TEXT_COLUMNS, SECRETS_DIR

parser = argparse.ArgumentParser(description="Process some flags.")
parser.add_argument("-b", "--build", action="store_true", help="Rebuild the model from scratch.")
parser.add_argument("-p", "--predict", action="store_true", help="Predict the label of the data.")
args = parser.parse_args()


def main():
    # file_path = os.path.join(os.getcwd(), "private/budget.csv")
    file_path = f"{SECRETS_DIR}/private/budget.csv"
    id_to_label = {e.value: e.name for e in Tags}

    # Load and preprocess data
    data = load_data(file_path, is_rebuild_bert_embds=True)
    train_features, test_features, train_labels, test_labels = split_data(data.drop(columns='label'), data['label'])

    if args.build:
        train_data = pd.concat([train_features, train_labels], axis = 1)
        test_data = pd.concat([test_features, test_labels], axis = 1)
        train_dataloader = create_dataloader(train_data, NUMERIC_COLUMNS, TEXT_COLUMNS, 'label', batch_size=32)
        test_dataloader = create_dataloader(test_data, NUMERIC_COLUMNS, TEXT_COLUMNS, 'label', batch_size=32)
        model = MultimodalModel()
        trainer = MultimodalTrainer(model=model, train_loader=train_dataloader, test_loader=test_dataloader, num_epochs=100)

        trainer.train()
        trainer.evaluate()
        trainer.save(MODEL_SAVE_DIRECTORY + "/saved_model.pth")

        # Get predictions
        y_true = test_labels.tolist()
        test_numeric_tensor = torch.tensor(test_data[NUMERIC_COLUMNS].values, dtype=torch.float32)
        test_text_tensor = torch.tensor(test_data[TEXT_COLUMNS].values, dtype=torch.float32)
        y_pred = trainer.predict(test_numeric_tensor, test_text_tensor).tolist()

        # Convert IDs back to label names
        y_true_labels = [id_to_label[y] for y in y_true]
        y_pred_labels = [id_to_label[y] for y in y_pred]

        # Compute confusion matrix
        plot_confusion_matrix(y_true_labels, y_pred_labels, list(id_to_label.values()))

        # Show mislabeled examples
        view_mislabeled_samples(test_features, y_true_labels, y_pred_labels)

    elif args.predict:
        trainer = MultimodalTrainer.load(MultimodalModel, MODEL_SAVE_DIRECTORY + "/saved_model.pth")
        test_numeric_tensor = torch.tensor(test_features[NUMERIC_COLUMNS].values, dtype=torch.float32)
        test_text_tensor = torch.tensor(test_features[TEXT_COLUMNS].values, dtype=torch.float32)
        y_pred = trainer.predict(test_numeric_tensor,test_text_tensor).tolist()
        y_pred = [id_to_label[y] for y in y_pred]
        print(y_pred[:10])
    else:
        print("Please provide a flag to either build or predict the model.")

def plot_confusion_matrix(y_true, y_pred, label_names):
    """Plot a confusion matrix using seaborn."""
    cm = confusion_matrix(y_true, y_pred, labels=label_names)

    plt.figure(figsize=(10, 7))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=label_names, yticklabels=label_names)
    plt.xlabel("Predicted Label")
    plt.ylabel("True Label")
    plt.title("Confusion Matrix")
    plt.savefig(f"{SECRETS_DIR}/private/saved_model/confusion_matrix.png")

    # save to file
    # df_cm = pd.DataFrame(cm, index=label_names, columns=label_names)
    # df_cm.to_csv("private/saved_model/confusion_matrix.csv")


def view_mislabeled_samples(features, y_true_labels, y_pred_labels):
    """Print out mislabeled test samples."""
    mislabeled_indices = [i for i in range(len(y_true_labels)) if y_true_labels[i] != y_pred_labels[i]]
    features = features[['amount_usd', 'year', 'month', 'day', 'description']]
    mislabeled_data = pd.DataFrame({
        "Text": [features.iloc[i].to_dict() for i in mislabeled_indices],
        "True Label": [y_true_labels[i] for i in mislabeled_indices],
        "Predicted Label": [y_pred_labels[i] for i in mislabeled_indices]
    })
    # save to file
    mislabeled_data.to_csv(f"{SECRETS_DIR}/private/saved_model/mislabeled_samples.csv", index=False)

if __name__ == "__main__":
    main()
