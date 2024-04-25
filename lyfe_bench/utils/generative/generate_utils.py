import os
import fnmatch
import numpy as np
import pandas as pd
from pathlib import Path
from openai.embeddings_utils import get_embedding
from agent.embedding_utils import load_embeddings


DATABASEPATH = Path(os.path.realpath(__file__)).parent / 'database'
environmentPATH = Path(os.path.realpath(__file__)).parent.parent / 'configs' / 'generative' / 'environment'
UNITYASSETPATH = Path(os.path.realpath(__file__)).parent.parent / 'unity' / 'GenAgentMinimal' / 'Assets'
UNITYWORLDPATH = UNITYASSETPATH / 'WorldMap'  # TODO: This is too specific
UNITYRESOURCEPATH = UNITYASSETPATH / 'Resources'
AGENTCONFIGPATH = Path(os.path.realpath(__file__)).parent.parent / 'configs' / 'agents'


def find_files_with_extensions(directory, extensions):
    file_names = list()
    relative_paths = list()

    for root, _, files in os.walk(directory):
        for extension in extensions:
            for file in fnmatch.filter(files, f'*{extension}'):
                file_name_without_extension, _ = os.path.splitext(file)
                relative_path = os.path.relpath(root, directory)
                file_names.append(file_name_without_extension)
                relative_paths.append(relative_path)

    return file_names, relative_paths


def get_resource_embeddings(redo=False):
    """For all resources in the Unity project, generate embeddings given their name."""
    df_path = DATABASEPATH / f'genagent_resource_embeddings.csv'
    if df_path.exists() and not redo:
        return load_embeddings(df_path)

    print("Generate embeddings for Unity Resources")
    directory_path = UNITYRESOURCEPATH
    extensions = ['.prefab', '.anim']
    file_names, relative_paths = find_files_with_extensions(directory_path, extensions)
    print(f"Found file names {file_names} in path {directory_path}")

    embeddings = list()
    for name in file_names:
        name = name.replace("_", " ")
        embedding = get_embedding(name, engine="text-embedding-ada-002")
        embeddings.append(embedding)

    data = {"path": [path + "/" + name for name, path in zip(file_names, relative_paths)],
            "name": file_names,
            "type": relative_paths,  # Relying on the names of subfolder for types
            "embedding": embeddings}

    df = pd.DataFrame(data=data)
    df.to_csv(df_path)
    return df
