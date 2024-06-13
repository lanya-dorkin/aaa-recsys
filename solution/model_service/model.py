import pickle
import math
import torch
import torch.nn as nn
import torch.nn.functional as F
import faiss
import numpy as np


class PositionalEncoding(nn.Module):
    def __init__(self, d_model, max_len=5000):
        super(PositionalEncoding, self).__init__()
        self.encoding = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model))
        self.encoding[:, 0::2] = torch.sin(position * div_term)
        self.encoding[:, 1::2] = torch.cos(position * div_term)
        self.encoding = self.encoding.unsqueeze(0).transpose(0, 1)
    
    def forward(self, x):
        return x + self.encoding[:x.size(0), :]

class TransRecModel(nn.Module):
    def __init__(self, item2id, d_model=128, nhead=8, num_layers=4, dim_feedforward=256, max_len=40):
        super(TransRecModel, self).__init__()
        self.embedding = nn.Embedding(len(item2id)+1, d_model, padding_idx=0)
        self.positional_encoding = PositionalEncoding(d_model, max_len)
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model, nhead=nhead, dim_feedforward=dim_feedforward,
            activation=F.gelu, batch_first=True
        )
        self.encoder = nn.TransformerEncoder(encoder_layer, num_layers)
        self.final_q = nn.Linear(d_model, 1)
        self.fc = nn.Linear(d_model, d_model)
    
    def forward(self, x):
        x = self.embedding(x)
        x = self.positional_encoding(x)
        x = self.encoder(x)
        # x = x.mean(dim=1)
        att = self.final_q(x)
        att = F.softmax(att, dim=1)
        x = torch.sum(x * att, dim=1)
        x = self.fc(x)
        return x
    

def load_model(item2id: dict, filename='model.pth') -> nn.Module:
    model = TransRecModel(item2id)
    model.load_state_dict(torch.load(f'data/{filename}', map_location=torch.device('cpu')))
    model.eval()

    return model


def load_artifacts() -> tuple[list, dict, dict]:
    with open('data/top_items.pkl', 'rb') as file:
        top_items = pickle.load(file)
    with open('data/item2id.pkl', 'rb') as file:
        item2id = pickle.load(file)
    id2item = {v: k for k, v in item2id.items()}

    return top_items, item2id, id2item


def get_faiss_index(item_embeddings: np.ndarray, ids: np.ndarray, dim: int = 128) -> faiss.IndexFlatIP:
    index = faiss.IndexFlatIP(dim)
    index = faiss.IndexIDMap(index)
    index.add_with_ids(item_embeddings[1:], ids)

    return index