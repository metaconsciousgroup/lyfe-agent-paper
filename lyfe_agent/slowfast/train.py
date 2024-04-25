import sys

sys.path.append("..")
sys.path.append("../..")
# sys.path.append("../../..")

import argparse
import json

import torch
import torch.nn as nn
import torch.optim as optim
import pytorch_lightning as pl
import random
from lyfe_agent.slowfast.model_utils import (
    data_augmentation,
    CustomDataModule,
    dataset_analysis,
)
from lyfe_agent.utils.encoder_utils import OpenAIEncoder
from lyfe_agent.slowfast.model import BaseMLP
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create a handler that writes log messages to the console
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)  # Set handler level to INFO

# Add the handler to the logger
logger.addHandler(handler)


class ModelSystem(pl.LightningModule):
    def __init__(self, model, lr=0.001):
        super(ModelSystem, self).__init__()
        self.model = model
        self.lr = lr
        self.criterion = nn.CrossEntropyLoss()

    def forward(self, x):
        return self.model(x)

    def configure_optimizers(self):
        optimizer = optim.Adam(self.model.parameters(), lr=self.lr)
        return optimizer

    def training_step(self, batch, batch_idx):
        x, y = batch
        outputs = self(x)
        loss = self.criterion(outputs, y)

        _, predicted = torch.max(outputs, 1)
        accuracy = (predicted == y).float().mean()
        self.log("train_loss", loss, prog_bar=True, on_step=True, on_epoch=True)
        self.log("train_accuracy", accuracy, prog_bar=True, on_step=True, on_epoch=True)
        return loss

    def validation_step(self, batch, batch_idx):
        x, y = batch
        outputs = self(x)
        loss = self.criterion(outputs, y)
        _, predicted = torch.max(outputs, 1)
        accuracy = (predicted == y).float().mean()
        self.log("val_loss", loss, prog_bar=True)
        self.log("val_accuracy", accuracy, prog_bar=True)
        return loss

    def test_step(self, batch, batch_idx):
        x, y = batch
        outputs = self(x)
        _, predicted = torch.max(outputs, 1)

        # Store inputs, ground truth, and predicted outputs
        if not hasattr(self, "test_results"):
            self.test_results = {"inputs": [], "ground_truth": [], "predictions": []}
        self.test_results["inputs"].append(x)
        self.test_results["ground_truth"].append(y)
        self.test_results["predictions"].append(predicted)

        accuracy = (predicted == y).float().mean()
        self.log("test_accuracy", accuracy)


# Create a parser for command-line arguments
parser = argparse.ArgumentParser(description="Training Slow/Fast")
parser.add_argument(
    "--dataset", type=str, default="from_sim", help="Name of the dataset file"
)
parser.add_argument(
    "--model-name",
    type=str,
    default="modelMLP",
    help="Name for the saved model",
)

# Parse the command-line arguments
args = parser.parse_args()


def filter_dict(d, keys):
    return {k: d[k] for k in keys if k in d}


# Main execution script
if __name__ == "__main__":
    # Note: After the project refactoring, this script no longer works. Update this if training is required.
    from pathlib import Path
    BASE_DIR = Path(__file__).resolve().parent
    MODELPATH = BASE_DIR / "models"
    dataset_path = BASE_DIR / f"experiments/core_executor/{args.dataset}.json"
    model_path = MODELPATH / f"core_executor/{args.model_name}.pt"

    with open(dataset_path, "r") as f:
        dataset = json.load(f)

    # TODO: new format from sim
    if "input" in dataset[0].keys():
        keys_to_keep = ["progress"]
        inputs = [filter_dict(d["input"], keys_to_keep) for d in dataset]
        labels = [sample["output"]["next_action"] for sample in dataset]
    else:
        inputs = dataset
        labels = [sample["next_action"] for sample in dataset]

    # Augment data
    # Use the new data_augmentation function
    inputs, labels = data_augmentation(inputs, labels, data_balance=False)

    # Preprocess data
    # This should be preprocessing from the Fast module itself
    openai_encoder = OpenAIEncoder(model_name="text-embedding-ada-002")

    # def preprocessing_inputs(inputs):
    #     inputs = [sample["goal"] + sample.get("observation", "") for sample in inputs]
    #     return openai_encoder(inputs)

    def preprocessing_inputs(inputs):
        new_inputs = list()
        for sample in inputs:
            progress = sample.get("progress", None)
            if not progress:
                new_inputs.append(sample["goal"])
            else:
                # last_smry = summary.split(".")[-2]
                new_inputs.append(progress)
        inputs_embd = openai_encoder(new_inputs)
        return inputs_embd, new_inputs

    inputs, inputs_original = preprocessing_inputs(inputs)

    # Print different labels with different colors
    for input, label in zip(inputs_original, labels):
        color = "\033[92m" if label == "talk" else "\033[91m"
        print(input, color + label + "\033[0m")

    unique_labels = set(labels)
    str_to_label = {label: idx for idx, label in enumerate(unique_labels)}
    datamodule = CustomDataModule(inputs, labels, split=0.5, batch_size=32)
    datamodule.prepare_data()

    model = BaseMLP(
        layer_sizes=[inputs.shape[1], len(unique_labels)],
        str_to_label=str_to_label,
    )
    model_system = ModelSystem(model=model)

    # Trainer
    trainer = pl.Trainer(limit_train_batches=100, max_epochs=20)
    trainer.fit(model_system, datamodule=datamodule)
    trainer.test(datamodule=datamodule)

    datamodule.display_most_common_label_proportions()

    # torch.save(model_system.state_dict(), model_path)
