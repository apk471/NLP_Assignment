import numpy as np
import re
import math
from collections import Counter, defaultdict
from langchain.embeddings.base import Embeddings


class SimpleEmbedding(Embeddings):
    """
    A simple from-scratch embedding class using TF-IDF.
    Produces dense numpy vectors for each text input.
    """

    def __init__(self, vocab=None, idf=None, dim=None):
        self.vocab = vocab or {}
        self.idf = idf or defaultdict(float)
        self.dim = dim or len(self.vocab)

    def _tokenize(self, text: str):
        text = text.lower()
        text = re.sub(r"[^a-z0-9\s]", " ", text)
        return [t for t in text.split() if t]

    def fit(self, documents):
        """
        Build vocabulary and compute IDF scores from documents.
        documents: list of str
        """
        print("[INFO] Building vocabulary from scratch...")
        doc_count = len(documents)
        df_counter = Counter()

        for doc in documents:
            tokens = set(self._tokenize(doc))
            for tok in tokens:
                df_counter[tok] += 1

        self.vocab = {word: i for i, (word, _) in enumerate(df_counter.items())}
        self.dim = len(self.vocab)

        self.idf = {
            word: math.log((doc_count + 1) / (df + 1)) + 1
            for word, df in df_counter.items()
        }

        print(f"[INFO] Vocab size: {self.dim}")

    def _tfidf_vector(self, text: str):
        vec = np.zeros(self.dim, dtype=np.float32)
        tokens = self._tokenize(text)
        if not tokens:
            return vec

        tf_counter = Counter(tokens)
        max_tf = max(tf_counter.values())

        for tok, tf in tf_counter.items():
            if tok in self.vocab:
                idx = self.vocab[tok]
                tf_weight = tf / max_tf
                idf_weight = self.idf.get(tok, 0.0)
                vec[idx] = tf_weight * idf_weight

        norm = np.linalg.norm(vec)
        if norm > 0:
            vec /= norm
        return vec

    def embed_documents(self, texts):
        return [self._tfidf_vector(t).tolist() for t in texts]

    def embed_query(self, text):
        return self._tfidf_vector(text).tolist()


def create_embeddings(all_documents_texts=None):
    """
    Create and train a custom TF-IDF embedding model from scratch.
    all_documents_texts: list of raw text documents to build vocab.
    """
    model = SimpleEmbedding()

    if all_documents_texts:
        model.fit(all_documents_texts)

    return model

if __name__ == "__main__":
    docs = [
        "This is a sample document.",
        "This document is another example.",
        "TF-IDF embeddings are useful for text representation."
        
    ]
    embedding_model = create_embeddings(docs)
    vecs = embedding_model.embed_documents(docs)
    for i, vec in enumerate(vecs):
        print(f"Document {i} vector: {vec}")
    query_vec = embedding_model.embed_query("sample text")
    print(f"Query vector: {query_vec}")