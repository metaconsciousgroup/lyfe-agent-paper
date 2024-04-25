import os
from datetime import datetime, timedelta
import pickle
import json
from omegaconf import DictConfig, OmegaConf
from pathlib import Path
import argparse

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import matplotlib.dates as mdates
from itertools import combinations
from sentence_transformers import SentenceTransformer, util
from scipy.cluster.hierarchy import dendrogram, linkage, fcluster
from scipy.spatial.distance import pdist
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
import re
import torch

import analysis
import  analysis.transformer_metrics
import analysis.analysis_utils as analysis_utils
from analysis.analysis_utils import process_hydra_folders_recursively
from analysis.conversation import post_process, get_summary, load_summary, add_hobby_pet_gender_to_summary
import analysis.plot_utils as plot_utils

def main(args):
    """
    Main function that orchestrates the execution of the analysis.

    Args:
        args (ArgumentParser): An argument parser object containing 
        the command line arguments.
    """

    # Processing the experiment logs and data
    post_process(EXPERIMENT_PATH)

    # Loading datasets
    log_df = pd.read_csv(EXPERIMENT_PATH / 'main_log.csv', index_col=0)
    conv_df = pd.read_csv(EXPERIMENT_PATH / 'conversation.csv', index_col=0)

    # Performing temporal analysis on the logs
    temporal_analysis(log_df)
    print("Finished Temporal Analysis")

    # Performing conversation analysis
    conversation_analysis(conv_df)
    print("Finished Conversation Analysis")

    # Performing agent memory analysis if specified in command line arguments
    if args.agent:
        agent_memory_analysis()
        print("Finished Agent Memory Analysis")


def temporal_analysis(log_df):
    """
    Perform temporal analysis on the log data. It generates line plots to represent 
    the counts of events and agents over time.

    Args:
        log_df (DataFrame): Log data frame which contains timestamp, events and agent data.
    """
    # Create a copy of the dataframe to avoid modifying the original one
    df = log_df.copy()
    time_column = 'timestamp'

    # Prepare the dataframe
    df[time_column] = pd.to_datetime(df[time_column]).dt.round('1min')

    # Analyze and plot event count over time
    df_grouped = df.groupby([time_column, 'event']).size().reset_index(name='counts')
    df_pivot = df_grouped.pivot(index=time_column, columns='event', values='counts').fillna(0)
    plot_and_save(df_pivot, 'Event Count Over Time', 'Event', 'Event Count', 'event_count_over_time.png')

    # Analyze and plot agent count over time
    df_grouped = df.groupby([time_column, 'agent']).size().reset_index(name='counts')
    df_pivot = df_grouped.pivot(index=time_column, columns='agent', values='counts').fillna(0)
    plot_and_save(df_pivot, 'Agent Count Over Time', 'Agent', 'Agent Count', 'agent_count_over_time.png')


def plot_and_save(df, title, legend_title, ylabel, filename):
    """
    Plot and save the data in the given DataFrame.

    Args:
        df (DataFrame): Data to plot.
        title (str): Plot title.
        legend_title (str): Legend title.
        ylabel (str): Y-axis label.
        filename (str): File name to save the plot.
    """
    df.plot(kind='line')
    plt.xlabel('Time')
    plt.ylabel(ylabel)
    plt.title(title)
    plt.legend(title=legend_title)

    # Ensure the directory exists
    os.makedirs(EXPERIMENT_PATH / 'simulation_analysis', exist_ok=True)

    # Save the figure
    plt.savefig(EXPERIMENT_PATH / f'simulation_analysis/{filename}')
    plt.close()




def conversation_analysis(conv_df):
    """
    Perform conversation analysis on the conversation data. It calculates metrics, 
    creates plots for distributions and histograms of various features.

    Args:
        conv_df (DataFrame): Conversation data frame which contains messages.
    """
    # Calculate or read metrics
    metrics_df = get_or_calculate_metrics(conv_df)

    # Ensure the directory exists
    output_dir = EXPERIMENT_PATH / 'transformer_analysis'
    os.makedirs(output_dir, exist_ok=True)

    # Define the metric lists and corresponding names for distribution plots
    dist_metrics = [('Emotions', EMOTIONS), ('Topics', TOPICS)]
    for metric_name, metric_list in dist_metrics:
        plot_distribution(metrics_df[metric_list], metric_name, output_dir)

    # Define the metric lists and corresponding names for histogram plots
    hist_metrics = [('Toxicity', TOXICITY), ('Sentiment', SENTIMENT), ('Irony', IRONY), ('Coherence', COHERENCE)]
    for metric_name, metric_list in hist_metrics:
        plot_histogram(metrics_df, metric_list, metric_name, output_dir)


def get_or_calculate_metrics(conv_df):
    """
    Calculate or read transformer metrics.

    Args:
        conv_df (DataFrame): Conversation data frame which contains messages.

    Returns:
        DataFrame: DataFrame containing the metrics.
    """
    metrics_file = EXPERIMENT_PATH / 'metrics.csv'
    if metrics_file.is_file():
        metrics_df = pd.read_csv(metrics_file)
    else:
        metrics_df = analysis.transformer_metrics.calculate_metrics(list(conv_df['message']))
        metrics_df.to_csv(metrics_file, index=False)
    return metrics_df


def agent_memory_analysis():
    """
    Perform agent memory analysis on the agent memory data. It calculates and visualizes similarity matrices, 
    does hierarchical clustering, and does dimensionality reduction for visualization.

    """
    # Load agent memory data
    memory_data = load_agent_memory_data()

    # Ensure the directory exists
    output_dir = EXPERIMENT_PATH / 'memory_analysis'
    os.makedirs(output_dir, exist_ok=True)

    # Save memory data for the selected agent
    save_memory_data(memory_data, output_dir, args.agent)

    # Initialize dimensionality reduction technique
    dim_reducer = PCA(n_components=2)

    # Initialize placeholders for storing all embeddings, labels, and index ranges
    all_embeddings, index_ranges, start_index = [], {}, 0

    # Process each memory type
    for memory_type, memories in memory_data.items():
        # Skip empty memories
        if not memories:
            continue

        # Encode memories to embeddings
        embeddings = SIMILARITY_MODEL.encode(memories, convert_to_tensor=True)

        # Analyze memories in the embedding space
        analyze_memories_in_embedding_space(embeddings,memories, memory_type, output_dir)

        # Perform and plot dimensionality reduction
        reduced_data = dim_reducer.fit_transform(embeddings)
        plot_reduced_embeddings(reduced_data, memory_type, output_dir)

        # Prepare data for combined similarity matrix
        all_embeddings.append(embeddings)
        index_ranges[memory_type] = (start_index, start_index + len(embeddings))
        start_index += len(embeddings)

    # Concatenate embeddings and calculate similarity matrix
    all_embeddings = torch.cat(all_embeddings, dim=0)
    similarity_matrix = util.pytorch_cos_sim(all_embeddings, all_embeddings)

    # Plot combined similarity matrix
    plot_combined_similarity_matrix(similarity_matrix, index_ranges, output_dir)


def load_agent_memory_data():
    """
    Load agent memory data from a JSON file.

    Returns:
        dict: Loaded agent memory data.
    """
    with open(EXPERIMENT_PATH / 'agent_memory.json', 'r') as file:
        data = json.load(file)
    agent = data[args.agent]
    memory_data = {
        "workmem": [s.split(": ", 1)[-1] if ": " in s else s for s in agent['workmem']],
        "recentmem": [s.split(": ", 1)[-1] if ": " in s else s for s in agent['recentmem']],
        "convomem": [s.split(": ", 1)[-1] if ": " in s else s for s in agent['convomem']],
        "longmem": [s.split(": ", 1)[-1] if ": " in s else s for s in agent['longmem']]
    }

    return memory_data


def save_memory_data(memory_data, output_dir, agent_name):
    """
    Save memory data to a JSON file.

    Args:
        memory_data (dict): Memory data to save.
        output_dir (Path): Output directory where the file will be saved.
        agent_name (str): Name of the agent.
    """
    with open(output_dir / f'{agent_name}_memories.json', 'w') as file:
        json.dump(memory_data, file, indent=4)


def analyze_memories_in_embedding_space(embeddings,memories, memory_type, output_dir):
    """
    Analyze memories in the embedding space. It calculates and plots similarity matrices, and does hierarchical clustering.

    Args:
        embeddings (Tensor): Embeddings of the memories.
        memory_type (str): Type of the memories.
        output_dir (Path): Output directory for the plots.
    """
    # Compute and plot similarity matrices
    similarity_scores = util.pytorch_cos_sim(embeddings, embeddings)
    plot_similarity_matrices(similarity_scores, memory_type, output_dir)

    # Compute and plot hierarchical clustering
    cluster_labels = plot_hierarchical_clustering(embeddings, memory_type, output_dir)

    # Generate clusters based on hierarchical analysis
    grouped_memories = []
    # For each unique label, find the embeddings that belong to that cluster and store them
    for label in np.unique(cluster_labels):
        grouped_memories.append([item for item, m in zip(memories, cluster_labels == label) if m])

    with open(output_dir / f"{memory_type}_groups.json", 'w') as file:
        json.dump(grouped_memories, file, indent=4)


def plot_distribution(df, metric_name, output_dir):
    """
    This function plots and saves the distribution of the max metric.

    Args:
        df (pandas.DataFrame): The DataFrame containing the data.
        metric_name (str): The name of the metric.
        output_dir (str): The directory path to save the image.
    """

    # Count the occurrence of each submetric
    counts = df.idxmax(axis=1).value_counts().reset_index()
    counts.columns = ['Submetric', 'Count']

    # Create a figure and axes
    plt.figure(figsize=(10, 6))

    # Create the plot
    sns.barplot(x='Count', y='Submetric', data=counts, palette='viridis')

    # Customize the plot
    plt.title(f'Distribution of Max {metric_name}', fontsize=16)
    plt.xlabel('Count', fontsize=13)
    plt.ylabel(metric_name, fontsize=13)
    plt.xticks(fontsize=11)
    plt.yticks(fontsize=11)

    # Save the figure
    plt.savefig(Path(output_dir) / f"{metric_name}_distribution.png", bbox_inches='tight', dpi=300)

    # Close the plot
    plt.close()


def plot_histogram(metrics_df, metric_list, metric_name, output_dir):
    """
    This function plots and saves the histogram of the metric.

    Args:
        metrics_df (pandas.DataFrame): The DataFrame containing the data.
        metric_list (list): The list of metrics.
        metric_name (str): The name of the metric.
        output_dir (str): The directory path to save the image.
    """

    # Create a figure
    plt.figure(figsize=(10, 6))

    # Create the overlaid histograms for each submetric
    for submetric in metric_list:
        sns.histplot(metrics_df[submetric], kde=True, label=submetric)

    # Customize the plot
    plt.title(f'Distribution of {metric_name}', fontsize=16)
    plt.xlabel('Values', fontsize=13)
    plt.ylabel('Frequency', fontsize=13)
    plt.legend(loc='upper right')
    plt.xticks(fontsize=11)
    plt.yticks(fontsize=11)

    # Save the figure
    plt.savefig(Path(output_dir) / f"{metric_name}_histogram.png", bbox_inches='tight', dpi=300)

    # Close the plot
    plt.close()


def plot_similarity_matrices(similarity_scores, memory_type, output_dir):
    """
    This function plots and saves the heatmap and clustermap of similarity scores.

    Args:
        similarity_scores (torch.Tensor): The similarity scores of embeddings.
        memory_type (str): The type of the memory.
        output_dir (str): The directory path to save the images.
    """

    # Create a heatmap
    plt.figure(figsize=(10, 10))
    sns.heatmap(similarity_scores, annot=False, square = True)
    plt.savefig(f'{output_dir}/{memory_type}_heatmap.png')
    plt.close()

    # Create a clustermap
    cmap = sns.diverging_palette(230, 20, as_cmap=True)
    g = sns.clustermap(similarity_scores, cmap=cmap, vmax=1, vmin=-1, center=0, linewidths=.5, cbar_kws={"shrink": 0.5})
    g.fig.savefig(f'{output_dir}/{memory_type}_clustermap.png')
    plt.close()

def plot_combined_similarity_matrix(similarity_matrix, index_ranges, output_dir):
    """
    This function plots a combined similarity matrix, saves and shows the heatmap and clustermap.
    
    Args:
        similarity_matrix (torch.Tensor): The similarity matrix of all vectors.
        index_ranges (dict): A dictionary where keys are memory_types and values are tuple of index ranges.
        output_dir (str): The directory path to save the heatmap and clustermap images.
    """

    # Initialize plot and colormap specifications
    fig, ax = plt.subplots(figsize=(10, 10))
    cmaps = ['Blues', 'Reds', 'Greens', 'Purples', 'Greys']
    patches = []

    # Generate masked heatmap for each memory type and colormap
    for (label, (start, end)), cmap in zip(index_ranges.items(), cmaps):
        mask = np.triu(np.ones_like(similarity_matrix, dtype=bool))
        mask[start:end, start:end] = False
        sns.heatmap(similarity_matrix, mask=mask, cmap=cmap, cbar=False, center=0.0, square=True)
        patches.append(mpatches.Patch(color=sns.color_palette(cmap)[2], label=label))

    # Final heatmap for the upper triangle
    mask = np.triu(np.ones_like(similarity_matrix, dtype=bool))
    sns.heatmap(similarity_matrix, mask=mask, square=True, cmap='Oranges', linewidths=0.7, cbar_kws={"shrink": 0.5})

    # Add legend and save the heatmap
    plt.legend(handles=patches, bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
    plt.savefig(f"{output_dir}/combined_heatmap.png")
    plt.close()

    # Generate and save the clustermap
    cmap = sns.diverging_palette(230, 20, as_cmap=True)
    clustermap = sns.clustermap(similarity_matrix, cmap=cmap, vmax=1, vmin=-1, center=0, linewidths=.5, cbar_kws={"shrink": 0.5})
    plt.title('Visualization for All Memories')
    clustermap.savefig(f"{output_dir}/combined_clustermap.png")
    plt.close()
    
def plot_hierarchical_clustering(embeddings, memory_type, output_dir):
    """
    This function performs hierarchical clustering on embeddings and saves the dendrogram.

    Args:
        embeddings (numpy.ndarray): The embeddings for clustering.
        memory_type (str): The type of the memory.
        output_dir (str): The directory path to save the image.
    """

    # Calculate the distance between each sample
    dist = pdist(embeddings, metric='cosine')

    # Create a linkage matrix
    linkage_matrix = linkage(dist, 'ward')

    # Create a figure
    fig = plt.figure(figsize=(8,8))

    # Plot the dendrogram
    dendro = dendrogram(linkage_matrix)
    plt.savefig(f'{output_dir}/{memory_type}_dendrogram.png')
    plt.close()

    # Find an optimal 't' that results in a desirable number of clusters (between 2 and 5)
    t_values = np.linspace(0, 5, num=11)  # You might want to adjust the range and step size
    for t in t_values:
        cluster_labels = fcluster(linkage_matrix, t, criterion='distance')
        if 2 <= len(set(cluster_labels)) <= 5:
            break

    return cluster_labels


def plot_reduced_embeddings(embeddings, memory_type, output_dir):
    # Convert to DataFrame for easier plotting
    df = pd.DataFrame(embeddings, columns=['x', 'y'])

    # Create a scatter plot
    plt.figure(figsize=(6, 6))

    # Create a sequence array based on the order of the memories
    sequence = np.arange(len(df))

    # Plot the scatter points with colors based on the sequence
    scatter = plt.scatter(df['x'], df['y'], c=sequence, cmap='viridis')
    plt.title(f'Visualization for {memory_type}')

    # Add a colorbar
    colorbar = plt.colorbar(scatter)
    colorbar.set_label('Progress of Memories')

    # Save the plot
    plt.savefig(f"{output_dir}/{memory_type}_scatter.png")
    plt.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='This is my analysis script.')
    parser.add_argument('-p', '--path', help='Path to the file to analyze', required=True)
    parser.add_argument('-s', '--save-figs', help='Save figures', default=True, type=bool)
    parser.add_argument('-a', '--analysis', help='Type of analysis', choices=['memory', 'conversations', 'all'], default='all')
    parser.add_argument('--agent', type=str, help='Agent to analyze', required=False)

    args = parser.parse_args()

    #Path where all analysis will be saved
    EXPERIMENT_PATH = Path(args.path)

    SIMILARITY_MODEL = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

    # Define your lists here
    EMOTIONS = ['admiration', 'curiosity', 'approval', 'confusion', 'gratitude', 'remorse', 'caring', 'sadness', 'love', 'optimism', 'joy', 'excitement',
                'disapproval', 'realization', 'neutral', 'disappointment', 'desire', 'surprise', 'relief', 'nervousness', 'grief', 'amusement', 'annoyance',
                'fear', 'embarrassment', 'anger', 'pride', 'disgust']

    MEMORIES = ['workmem', 'recentmem', 'longmem']

    TOPICS = [
            'diaries_&_daily_life', 'relationships', 'other_hobbies', 'celebrity_&_pop_culture', 'family', 
            'news_&_social_concern', 'film_tv_&_video', 'arts_&_culture', 'sports', 'travel_&_adventure', 
            'business_&_entrepreneurs', 'youth_&_student_life', 'learning_&_educational', 'gaming', 'science_&_technology',
            'music', 'fashion_&_style', 'food_&_dining', 'fitness_&_health'
    ]

    TOXICITY = ['toxic'] #non-toxic

    SENTIMENT  = ['POSITIVE', 'sentiment_nltk'] #NEGATIVE

    IRONY = ['irony'] #non-irony

    COHERENCE = ['mild gibberish', 'clean', 'word salad', 'noise']

    main(args)
