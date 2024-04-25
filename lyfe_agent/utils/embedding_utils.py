"""Utils for embeddings."""
import pandas as pd
import numpy as np
import openai
from openai.embeddings_utils import get_embedding
from typing import List, Union
import os
from sklearn.metrics.pairwise import cosine_similarity
import json

def load_embeddings(path):
    df = pd.read_csv(path)
    # Convert to np.array
    df["embedding"] = df.embedding.apply(eval).apply(np.array)
    return df


def save_embeddings(df, path):
    df.to_csv(path, index=False)


class BaseEmbeddingMatcher:
    """
    Base class for matching based on embeddings.
    """

    def __init__(self, filepath, nonces):
        """
        Initialize the matcher with an optional filepath to an existing embeddings file.
        """
        self.get_embedding = lambda query: get_embedding(
            query.replace("_", " "), engine="text-embedding-ada-002"
        )
        self.filepath = filepath

        if os.path.exists(filepath):
            with open(filepath, "r") as file:
                self.embeddings = json.load(file)
        else:
            self.embeddings = {}
        self.nonces = nonces

    def save_embeddings(self):
        """
        Save the current embeddings to a json file specified by self.filepath.
        """
        with open(self.filepath, "w") as file:
            json.dump(self.embeddings, file)

    def get_best_match(self, s):
        """
        Given a string s or a list of strings, compute its embedding and find the entry in self.embeddings that has the most similar embedding.
        Return the most similar entry and the cosine similarity score.
        """
        s_key = "/".join(s) if isinstance(s, list) else s

        if s_key in self.embeddings.keys():
            return s_key, 1.0

        # TODO: it is possible that OpenAI failed to compute the embedding for s_key
        try:
            if s_key in self.nonces:
                return None, None
            s_embedding = self.get_embedding(s_key)
        except:
            return None, None

        embeddings_to_compare = {
            k: v for k, v in self.embeddings.items() if k in self.entry_list
        }
        similarities = cosine_similarity(
            [s_embedding], list(embeddings_to_compare.values())
        )[0]

        best_match_index = np.argmax(similarities)
        best_match_entry = list(embeddings_to_compare.keys())[best_match_index]
        best_match_score = similarities[best_match_index]

        return best_match_entry, best_match_score

    def set_keys(self, new_entries):
        """
        This method should be overridden by subclasses.
        """
        raise NotImplementedError


class StringEmbeddingMatcher(BaseEmbeddingMatcher):
    """
    Matches single strings based on their embeddings.
    """

    def set_keys(self, new_strings):
        """
        Update the list of strings and their embeddings.
        """
        self.entry_list = new_strings

        for s in self.entry_list:
            if s not in self.embeddings.keys():
                self.embeddings[s] = self.get_embedding(s)
        self.save_embeddings()


class StringListEmbeddingMatcher(BaseEmbeddingMatcher):
    """
    Matches lists of strings based on their embeddings.
    """

    def set_keys(self, new_string_lists):
        """
        Update the list of string lists and their embeddings.
        """
        self.entry_list = ["/".join(sl) for sl in new_string_lists]

        for sl in new_string_lists:
            s_for_embedding = " of ".join(sl[::-1])
            sl_key = "/".join(sl)

            if sl_key not in self.embeddings.keys():
                self.embeddings[sl_key] = self.get_embedding(s_for_embedding)
        self.save_embeddings()
