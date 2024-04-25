import torch
import torch.nn as nn
import torch.optim as optim


class BaseMLP(nn.Module):
    def __init__(
        self,
        layer_sizes,
        str_to_label=None,
    ):
        super(BaseMLP, self).__init__()
        
        # Ensure layer_sizes has at least 2 values (input and output sizes)
        assert len(layer_sizes) > 1, "Layer sizes list should have at least two values."

        layers = []
        for i in range(len(layer_sizes) - 1):
            # Linear Layer
            layers.append(nn.Linear(layer_sizes[i], layer_sizes[i+1]))
            # Add Layer Normalization before activation
            if i < len(layer_sizes) - 2:  # No normalization or activation after the last linear layer
                layers.append(nn.LayerNorm(layer_sizes[i+1]))
            # Activation
            if i < len(layer_sizes) - 2:  # No activation after the last linear layer
                layers.append(nn.LeakyReLU())

        # Softmax for classification, assuming the output layer is used for classification purposes.
        layers.append(nn.Softmax(dim=1))

        self.layers = nn.Sequential(*layers)
        self.str_to_label = str_to_label
        self.label_to_str = (
            {v: k for k, v in str_to_label.items()} if str_to_label else None
        )

    def forward(self, x: torch.Tensor):
        return self.layers(x)

    def predict(self, x: torch.Tensor, possible_actions=None):
        """Predict the label of the input."""
        with torch.no_grad():
            probabilities = self(x)
            # probabilities = torch.nn.functional.softmax(outputs, dim=1)

            if possible_actions:
                # Convert the possible labels to their corresponding indices
                possible_indices = [
                    idx
                    for str, idx in self.str_to_label.items()
                    if str in possible_actions
                ]
                # Filter probabilities to only include possible labels
                probabilities = probabilities[0, possible_indices]

                # Get the index of the maximum probability among the possible labels
                max_idx = torch.argmax(probabilities).item()
                predicted_label = self.label_to_str[possible_indices[max_idx]]
            else:
                max_idx = torch.argmax(probabilities).item()
                predicted_label = self.label_to_str[max_idx]

            return predicted_label, probabilities[max_idx].item()


# class BaseRNN(nn.Module):
#     def __init__(
#         self,
#         input_size,
#         hidden_size,
#         output_size,
#         num_layers=1,
#         bidirectional=False,
#         str_to_label=None,
#         embedding_model_name=None,
#     ):
#         super(BaseRNN, self).__init__()

#         self.input_size = input_size
#         self.output_size = output_size

#         # keep track of which embedding model was used for training this model
#         assert embedding_model_name in [
#             "openai",
#             "sentence_transformer",
#         ], "Embedding model name must be either 'openai' or 'sentence_transformer'"
#         self.embedding_model_name = embedding_model_name

#         # Define RNN layers
#         self.rnn = nn.RNN(
#             input_size=input_size,
#             hidden_size=hidden_size,
#             num_layers=num_layers,
#             bidirectional=bidirectional,
#             batch_first=True,
#         )

#         # If the RNN is bidirectional, it will produce `2*hidden_size` outputs.
#         rnn_out_size = 2 * hidden_size if bidirectional else hidden_size

#         self.fc = nn.Linear(rnn_out_size, output_size)
#         self.softmax = nn.Softmax(dim=1)

#         self.str_to_label = str_to_label
#         self.label_to_str = (
#             {v: k for k, v in str_to_label.items()} if str_to_label else None
#         )

#     def forward(self, x: torch.Tensor):
#         rnn_out, _ = self.rnn(x)
#         # Use the last output of the RNN for classification
#         out = self.fc(rnn_out)
#         return self.softmax(out)

#     def predict(self, x: torch.Tensor, possible_actions=None):
#         """Predict the label of the input."""
#         with torch.no_grad():
#             probabilities = self.__call__(x)

#             if possible_actions:
#                 # Convert the possible labels to their corresponding indices
#                 possible_indices = [
#                     idx
#                     for str, idx in self.str_to_label.items()
#                     if str in possible_actions
#                 ]
#                 # Filter probabilities to only include possible labels
#                 probabilities = probabilities[0, possible_indices]

#                 # Get the index of the maximum probability among the possible labels
#                 max_idx = torch.argmax(probabilities).item()
#                 predicted_label = self.label_to_str[possible_indices[max_idx]]
#             else:
#                 max_idx = torch.argmax(probabilities).item()
#                 predicted_label = self.label_to_str[max_idx]

#             return predicted_label, probabilities[max_idx].item()
