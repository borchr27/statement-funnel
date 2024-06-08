from data_loader import load_data, preprocess_data, split_data, create_dataloaders
from model import BertTextClassifier
import os

if __name__ == '__main__':
    save_directory = os.path.join(os.getcwd(), 'private/saved_model')
    file_path = os.path.join(os.getcwd(), 'private/Budget-9-text.csv')

    # Load and preprocess data
    data = load_data(file_path)
    texts, labels, label_to_id = preprocess_data(data)
    train_texts, test_texts, train_labels, test_labels = split_data(texts, labels)

    # Initialize model if you want to train from scratch else load it
    num_labels = len(label_to_id)
    if os.path.exists('private/saved_model'):
        model = BertTextClassifier.load('private/saved_model')
    else:
        model = BertTextClassifier(num_labels)

    # Create dataloaders
    train_dataloader, test_dataloader = create_dataloaders(
        train_texts, train_labels, test_texts, test_labels, model.tokenize_data
    )

    if not os.path.exists('private/saved_model'):
        # Train the model
        model.train(train_dataloader)

        # Save the model
        model.save(save_directory)
        print(f"Model saved to {save_directory}")

    # Evaluate the model
    accuracy = model.evaluate(test_dataloader)
    print(f'Test Accuracy: {accuracy}')
