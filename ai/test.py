# from model import BertEmbeddings
#
# embedder = BertEmbeddings()
#
# # ✅ Multiple sentences embedding with CLS token
# batch_embeddings = embedder.get_bert_embedding(["Hello world!", "BERT embeddings are cool!"], pooling="cls")
# print(batch_embeddings.shape)  # Expected: (2, 768)
import os

from ai.data_loader import load_data

# import a csv to pandas
# import pandas as pd
# df = pd.read_csv("private/budget.csv")
#
# # look at the description column and determine the longest string length
# max_len = df['description'].str.len().max()
# print(max_len)  # Expected: 77
#

file_path = os.path.join(os.getcwd(), "private/budget.csv")

# Load and preprocess data
data = load_data(file_path)
print(data.head())