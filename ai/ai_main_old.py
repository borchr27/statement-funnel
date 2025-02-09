import argparse
import os

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from sklearn.metrics import confusion_matrix

os.environ["ENV"] = ".env.json"

from ai.data_loader import load_data, preprocess_data, split_data, create_dataloaders
from ai.old_model import BertTextClassifier
from program.constants import Tags

parser = argparse.ArgumentParser(description="Process some flags.")
parser.add_argument("-b", "--build", action="store_true", help="Rebuild the model from scratch.")
parser.add_argument("-p", "--predict", action="store_true", help="Predict the label of the data.")
args = parser.parse_args()


def main():
    save_directory = os.path.join(os.getcwd(), "private/saved_model")
    file_path = os.path.join(os.getcwd(), "private/budget.csv")

    # Load and preprocess data
    data = load_data(file_path)
    features, labels, label_to_id = preprocess_data(data)
    train_features, test_features, train_labels, test_labels = split_data(features, labels)

    for tag, label in zip(Tags, label_to_id.items()):
        assert tag.name == label[0], f"Tag name mismatch: {tag.name} != {label[0]}"
        assert tag.value == label[1], f"Tag value mismatch: {tag.value} != {label[1]}"
    print("Tags are matched.")

    # Initialize model if you want to train from scratch else load the model
    num_labels = len(label_to_id)
    if args.build:
        model = BertTextClassifier(num_labels)
        # Create dataloaders
        train_dataloader, test_dataloader = create_dataloaders(
            train_features, train_labels, test_features, test_labels, model.tokenize_data
        )
        # Train the model
        model.train(train_dataloader, epochs=18)

        # Save the model
        model.save(save_directory)
        print(f"Model saved to {save_directory}")

        # Get predictions
        y_true = test_labels
        y_pred = model.predict(test_features)

        # Convert IDs back to label names
        id_to_label = {v: k for k, v in label_to_id.items()}
        y_true_labels = [id_to_label[y] for y in y_true]
        y_pred_labels = [id_to_label[y] for y in y_pred]

        # Compute confusion matrix
        plot_confusion_matrix(y_true_labels, y_pred_labels, list(label_to_id.keys()))

        # Show mislabeled examples
        view_mislabeled_samples(test_features, y_true_labels, y_pred_labels)

    elif args.predict:
        model = BertTextClassifier.load("private/saved_model")
        predictions = model.predict(train_features)
        predicted_labels = [list(label_to_id.keys())[list(label_to_id.values()).index(pred)] for pred in predictions]
        print(predicted_labels)
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
    plt.savefig("private/saved_model/confusion_matrix.png")

    # save to file
    # df_cm = pd.DataFrame(cm, index=label_names, columns=label_names)
    # df_cm.to_csv("private/saved_model/confusion_matrix.csv")


def view_mislabeled_samples(features, y_true_labels, y_pred_labels):
    """Print out mislabeled test samples."""
    mislabeled_indices = [i for i in range(len(y_true_labels)) if y_true_labels[i] != y_pred_labels[i]]

    mislabeled_data = pd.DataFrame({
        "Text": [features[i] for i in mislabeled_indices],
        "True Label": [y_true_labels[i] for i in mislabeled_indices],
        "Predicted Label": [y_pred_labels[i] for i in mislabeled_indices]
    })
    # save to file
    mislabeled_data.to_csv("private/saved_model/mislabeled_samples.csv", index=False)

if __name__ == "__main__":
    main()
