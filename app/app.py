import streamlit as st
import numpy as np
import pickle
import torch
from models.helper import Skipgram, SkipgramNeg, Glove, CustomGensim
import nltk
nltk.download('brown')
from nltk.corpus import brown

# Load models
def load_models():
    # Skipgram
    with open('models/w2v-skipgram.args', 'rb') as skg_args_file:
        skg_args = pickle.load(skg_args_file)
    model_skipgram = Skipgram(**skg_args)
    model_skipgram.load_state_dict(torch.load('models/w2v-skipgram.model'))
    
    # Skipgram with Negative Sampling
    with open('models/w2v-skipgram-neg.args', 'rb') as neg_args_file:
        neg_args = pickle.load(neg_args_file)
    model_neg = SkipgramNeg(**neg_args)
    model_neg.load_state_dict(torch.load('models/w2v-skipgram-neg.model'))
    
    # GloVe
    with open('models/glove.args', 'rb') as glove_args_file:
        glove_args = pickle.load(glove_args_file)
    model_glove = Glove(**glove_args)
    model_glove.load_state_dict(torch.load('models/glove.model'))
    
    # Gensim
    with open('models/gensim.model', 'rb') as gensim_file:
        load_model = pickle.load(gensim_file)
    model_gensim = CustomGensim(load_model)
    
    return model_skipgram, model_neg, model_glove, model_gensim

# Load corpus
# corpus = brown.sents(categories="news")
corpus = list(brown.sents(categories="news"))

def similar_context(vector_list, single_vector, k=10):
    similarities = np.dot(vector_list, single_vector) / (np.linalg.norm(vector_list, axis=1) * np.linalg.norm(single_vector))
    top_indices = np.argsort(similarities)[-k:][::-1]
    return top_indices

# Initialize models
model_skipgram, model_neg, model_glove, model_gensim = load_models()
model_dict = {
    'Word2Vec (Skipgram)': model_skipgram,
    'Word2Vec (Negative Sampling)': model_neg,
    'GloVe (Sketch)': model_glove,
    'GloVe (Gensim)': model_gensim
}

# Streamlit UI
st.title("A1: That's what I like!")
st.write("Word Embedding Search Engine")    
query = st.text_input("Enter a search query")
model_name = st.selectbox("Select a Model", list(model_dict.keys()))

if st.button("Search"):
    if query:
        model = model_dict[model_name]
        qwords = query.split()
        qwords_embeds = np.array([np.array(model.get_embed(word)) for word in qwords if word])
        qsentence_embeds = np.mean(qwords_embeds, axis=0) if qwords_embeds.size else np.zeros(len(qwords_embeds[0]))
        
        corpus_embeds = []
        for each_sent in corpus:
            words_embeds = np.array([np.array(model.get_embed(word)) for word in each_sent if word])
            sentence_embeds = np.mean(words_embeds, axis=0) if words_embeds.size else np.zeros(len(words_embeds[0]))
            corpus_embeds.append(sentence_embeds)
        
        corpus_embeds = np.array(corpus_embeds)
        result_idxs = similar_context(corpus_embeds, qsentence_embeds)
        result = [' '.join(corpus[idx]) for idx in result_idxs]
        
        st.subheader(f"Displaying results by using {model_name}:")
        for sent in result:
            st.write(sent)
