import os
import pickle
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import faiss
import numpy as np
import torch
from model import TransRecModel, load_model, load_artifacts, get_faiss_index


app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')

top_items, item2id, id2item = load_artifacts()
model = load_model(item2id)

item_embeddings = model.embedding.weight.detach().cpu().numpy()
ids = np.array(list(id2item.values()))
index = get_faiss_index(item_embeddings, ids)


def pad_sequences(sequences: list[list[int]], max_len: int = 40) -> torch.tensor:
    """Pad sequences to the same length."""
    padded_sequences = []
    for seq in sequences:
        # for i in range(len(seq)):
        #     if seq[i] not in id2item:
        #         seq[i] = 0
        seq = [item2id.get(item, 0) for item in seq]
        if len(seq) < max_len:
            seq = seq + [0] * (max_len - len(seq))
        else:
            seq = seq[-max_len:]
        padded_sequences.append(seq)
    return torch.tensor(padded_sequences, dtype=torch.long)

def make_prediction(history: list[int] | list[list[int]], k=60) -> list[list[int]]:
    """Make prediction for a user or batch of users"""
    if not isinstance(history[0], list):
        history = [history]

    history = pad_sequences(history)
    
    with torch.no_grad():
        # user_vectors = model(history).detach().cpu().numpy()
        
        # workaround as model has a problem with encoder
        # but still learned useful embeddings
        user_vectors = model.embedding(history).sum(axis=1).detach().cpu().numpy()
        non_zero_items = (history > 0).sum(axis=1).detach().cpu().numpy()
    
        for i, (vec, n_items) in enumerate(zip(user_vectors, non_zero_items)):
            user_vectors[i] = vec / n_items

    _, item_ids = index.search(user_vectors, k=k)

    return [[int(item) for item in items] for items in item_ids]


@app.route('/get_prediction', methods=['POST'])
def get_user():
    history = request.get_json()
    if not history:
        preds = [0 for _ in range(60)]
        return jsonify({'predictions': preds}), 200

    sorted_history = sorted(history, key=lambda x: x['event_date'])

    try:
        preds = make_prediction([item['item_id'] for item in sorted_history])[0]
    except Exception as e:
        print(e)
        return jsonify({'message': 'Something went wrong'}), 500

    # workaround for users without model predictions
    for i in range(len(preds)):
        if preds[i] == -1 or preds[i] == 0:
            preds[i] = int(top_items[i])

    return jsonify({'predictions': preds}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.environ.get('MODEL_SERVICE_PORT'), debug=True)
