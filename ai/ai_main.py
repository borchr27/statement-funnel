from data_loader import load_data, preprocess_data, split_data, create_dataloaders
from model import BertTextClassifier
import os
import argparse


def main():
    parser = argparse.ArgumentParser(description="Process some flags.")
    parser.add_argument('-r', '--rebuild', action='store_true', help='Rebuild the model from scratch.')

    args = parser.parse_args()

    if args.rebuild:
        print("Rebuild flag is set!")
    else:
        print("Rebuild flag is not set.")

    save_directory = os.path.join(os.getcwd(), 'private/saved_model')
    file_path = os.path.join(os.getcwd(), 'private/Budget-9-text.csv')

    # Load and preprocess data
    data = load_data(file_path)
    texts, labels, label_to_id = preprocess_data(data)
    train_texts, test_texts, train_labels, test_labels = split_data(texts, labels)

    # Initialize model if you want to train from scratch else load it
    num_labels = len(label_to_id)
    if args.rebuild or not os.path.exists('private/saved_model'):
        model = BertTextClassifier(num_labels)
    else:
        model = BertTextClassifier.load('private/saved_model')

    # Create dataloaders
    train_dataloader, test_dataloader = create_dataloaders(
        train_texts, train_labels, test_texts, test_labels, model.tokenize_data
    )

    if args.rebuild or not os.path.exists('private/saved_model'):
        # Train the model
        model.train(train_dataloader, epochs=13)

        # Save the model
        model.save(save_directory)
        print(f"Model saved to {save_directory}")

    # Evaluate the model
    accuracy = model.evaluate(test_dataloader)
    print(f'Test Accuracy: {accuracy}')


if __name__ == '__main__':
    main()
