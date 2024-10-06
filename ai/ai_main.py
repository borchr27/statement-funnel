from data_loader import load_data, preprocess_data, split_data, create_dataloaders
from model import BertTextClassifier
import os
import argparse
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
        accuracy = model.evaluate(test_dataloader)
        print(f"Accuracy: {accuracy}")
    elif args.predict:
        model = BertTextClassifier.load("private/saved_model")
        predictions = model.predict(train_features)
        predicted_labels = [list(label_to_id.keys())[list(label_to_id.values()).index(pred)] for pred in predictions]
        print(predicted_labels)
    else:
        print("Please provide a flag to either build or predict the model.")


if __name__ == "__main__":
    main()
