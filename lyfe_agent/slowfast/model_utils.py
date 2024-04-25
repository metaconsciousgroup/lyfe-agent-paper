from typing import List
import numpy as np
from sklearn.utils import shuffle
import random
from sklearn.model_selection import train_test_split
from typing import List, Dict, Any
from collections import defaultdict
from random import choices
import os
from pathlib import Path
import pandas as pd
import json
import torch
from torch import Tensor
from torch.utils.data import DataLoader, TensorDataset

from collections import defaultdict
from random import choices
import pytorch_lightning as pl


class CustomDataModule(pl.LightningDataModule):
    def __init__(
        self,
        data: np.array,
        labels: List[str],
        split: float = 0.2,
        batch_size: int = 16,
    ):
        super().__init__()
        self.data = data
        self.labels = labels
        self.split = split
        self.batch_size = batch_size

        self.train_dataset = None
        self.val_dataset = None
        self.test_dataset = None
        self.str_to_label = None

    def prepare_data(self):
        # Create a mapping from unique labels to integers
        unique_labels = set(self.labels)
        self.str_to_label = {label: idx for idx, label in enumerate(unique_labels)}
        labels = [self.str_to_label[label] for label in self.labels]

        # Normalize the data
        data = self.data / np.linalg.norm(self.data, axis=1).reshape(-1, 1)

        # Shuffle the data
        data, labels = shuffle(data, labels, random_state=1)

        # Split the data
        X_train, X_temp, y_train, y_temp = train_test_split(
            data, labels, test_size=self.split, random_state=1
        )
        X_val, X_test, y_val, y_test = train_test_split(
            X_temp, y_temp, test_size=0.5, random_state=1
        )

        # Convert to PyTorch tensors
        self.train_dataset = TensorDataset(
            torch.Tensor(X_train), torch.Tensor(y_train).long()
        )
        self.val_dataset = TensorDataset(
            torch.Tensor(X_val), torch.Tensor(y_val).long()
        )
        self.test_dataset = TensorDataset(
            torch.Tensor(X_test), torch.Tensor(y_test).long()
        )

    def train_dataloader(self):
        return DataLoader(self.train_dataset, batch_size=self.batch_size, shuffle=True)

    def val_dataloader(self):
        return DataLoader(self.val_dataset, batch_size=1000)

    def test_dataloader(self):
        return DataLoader(self.test_dataset, batch_size=1000)
    
    def get_most_common_label_proportion(self, dataset):
        # Extract labels from the dataset
        labels = [label.item() for _, label in dataset]
        
        # Count the occurrences of each label
        label_counts = defaultdict(int)
        for label in labels:
            label_counts[label] += 1
        
        # Get the count of the most common label
        most_common_count = max(label_counts.values())
        
        # Return the proportion of the most common label
        return most_common_count / len(labels)
    
    def display_most_common_label_proportions(self):
        train_prop = self.get_most_common_label_proportion(self.train_dataset)
        val_prop = self.get_most_common_label_proportion(self.val_dataset)
        test_prop = self.get_most_common_label_proportion(self.test_dataset)

        # Displaying
        print(f"Proportion of most common label in Training set: {train_prop:.2%}")
        print(f"Proportion of most common label in Validation set: {val_prop:.2%}")
        print(f"Proportion of most common label in Test set: {test_prop:.2%}")
        




def balance_dataset(
    inputs: List[Dict[str, Any]], labels: List[Any]
) -> (List[Dict[str, Any]], List[Any]):
    # Convert the dataset to a DataFrame
    df = pd.DataFrame({"input": inputs, "label": labels})

    # Determine the minimum sample size among all groups
    min_samples = df["label"].value_counts().min()

    # Sample each group
    balanced_df = (
        df.groupby("label")
        .apply(lambda x: x.sample(min_samples, replace=True))
        .reset_index(drop=True)
    )

    # Return the balanced inputs and labels
    return balanced_df["input"].tolist(), balanced_df["label"].tolist()


def data_augmentation(
    inputs: List[Dict[str, Any]],
    labels: List[Any],
    data_balance: bool = False,
    verbose: bool = False,
) -> (List[Dict[str, Any]], List[Any]):
    # Remove redundant samples
    unique_samples = {}
    for input_, label in zip(inputs, labels):
        key = (label, tuple(input_.items()))
        unique_samples[key] = (input_, label)

    unique_inputs, unique_labels = zip(*unique_samples.values())

    if data_balance:
        return balance_dataset(unique_inputs, unique_labels)
    else:
        return unique_inputs, unique_labels




def dataset_analysis(dataset: List[Dict[str, Any]], labels: List[Any]):
    # for each label, count the number of samples
    label_counts = {label: labels.count(label) for label in set(labels)}

    # print the label counts
    print("---------DATASET ANALYSIS-----------")
    print("Label Counts:")
    for label, count in label_counts.items():
        print(f"{label}: {count}")

    print(f"Total number of samples: {len(dataset)}")

    # calculate the chance of randomly guessing the correct label
    total_samples = len(dataset)
    max_count = max(label_counts.values())
    chance = max_count / total_samples
    print(f"Chance of guessing the correct label: {chance}")
    print("------------------------------------")
