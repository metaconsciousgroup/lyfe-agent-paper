from collections import deque
from sklearn.metrics.pairwise import cosine_similarity

from lyfe_agent.base import BaseState

class RepetitionDetector(BaseState):
    def __init__(self, max_size=20, similarity_threshold=0.9, max_repeats=3):
        self.similarity_threshold = similarity_threshold
        self.max_repeats = max_repeats
        self.content_history = deque(maxlen=max_size)

        # the flag for whether the agent is repeating in a loop
        self.is_repetitive = False

    def receive(self, new_input):
        if "encoder_interaction" in new_input:
            embeddings = [embedding for _, embedding in new_input["encoder_interaction"]]
            self.content_history.extend(embeddings)

    def update(self):
        if len(self.content_history) <= 1:
            self.is_repetitive = False
            return
        similarities = cosine_similarity([self.content_history[-1]], list(self.content_history)[:-1])
        num_repeats = sum(sim > self.similarity_threshold for sim in similarities[0])
        if num_repeats >= self.max_repeats:
            self.is_repetitive = True
            self.clear()
        else:
            self.is_repetitive = False    

    def clear(self):
        self.content_history.clear()