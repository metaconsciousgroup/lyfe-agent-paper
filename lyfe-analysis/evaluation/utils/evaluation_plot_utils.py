import os
import json
from pathlib import Path
import numpy as np
import pandas as pd
import math
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from sentence_transformers import SentenceTransformer, util
from scipy.cluster.hierarchy import dendrogram, linkage, fcluster
from scipy.spatial.distance import pdist
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
import re
import torch

# import evaluation.utils.transformer_metrics as transformer_metrics

SIMILARITY_MODEL = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# Define your lists here
EMOTIONS = [
    "admiration",
    "curiosity",
    "approval",
    "confusion",
    "gratitude",
    "remorse",
    "caring",
    "sadness",
    "love",
    "optimism",
    "joy",
    "excitement",
    "disapproval",
    "realization",
    "neutral",
    "disappointment",
    "desire",
    "surprise",
    "relief",
    "nervousness",
    "grief",
    "amusement",
    "annoyance",
    "fear",
    "embarrassment",
    "anger",
    "pride",
    "disgust",
]

MEMORIES = ["workmem", "recentmem", "longmem"]

TOPICS = [
    "diaries_&_daily_life",
    "relationships",
    "other_hobbies",
    "celebrity_&_pop_culture",
    "family",
    "news_&_social_concern",
    "film_tv_&_video",
    "arts_&_culture",
    "sports",
    "travel_&_adventure",
    "business_&_entrepreneurs",
    "youth_&_student_life",
    "learning_&_educational",
    "gaming",
    "science_&_technology",
    "music",
    "fashion_&_style",
    "food_&_dining",
    "fitness_&_health",
]

TOXICITY = ["toxic"]  # non-toxic

SENTIMENT = ["POSITIVE", "sentiment_nltk"]  # NEGATIVE

IRONY = ["irony"]  # non-irony

COHERENCE = ["mild gibberish", "clean", "word salad", "noise"]

sns.set()

###TEMPORAL ANALYSIS###


def temporal_analysis(path, **kwargs):
    """
    Perform temporal analysis on the log data. It generates line plots to represent
    the counts of events and agents over time.

    Args:
        log_df (DataFrame): Log data frame which contains timestamp, events and agent data.
    """
    # Create a copy of the dataframe to avoid modifying the original one
    df = pd.read_csv(path / "main_log.csv")
    time_column = "timestamp"

    # Prepare the dataframe
    df[time_column] = pd.to_datetime(df[time_column]).dt.round("1min")

    # Analyze and plot event count over time
    df_grouped = df.groupby([time_column, "event"]).size().reset_index(name="counts")
    df_pivot = df_grouped.pivot(
        index=time_column, columns="event", values="counts"
    ).fillna(0)
    plot_and_save(
        df_pivot,
        "Event Count Over Time",
        "Event",
        "Event Count",
        "event_count_over_time.png",
        path,
    )

    # Analyze and plot agent count over time
    df_grouped = df.groupby([time_column, "agent"]).size().reset_index(name="counts")
    df_pivot = df_grouped.pivot(
        index=time_column, columns="agent", values="counts"
    ).fillna(0)
    plot_and_save(
        df_pivot,
        "Agent Count Over Time",
        "Agent",
        "Agent Count",
        "agent_count_over_time.png",
        path,
    )

    # Bar plots of the distribution of agents' decisions
    plot_agent_decisions(
        df, path / "simulation_analysis", filename="agent_decisions.png"
    )
    plot_agent_events(df, path / "simulation_analysis", filename="agent_events.png")


def plot_and_save(df, title, legend_title, ylabel, filename, path):
    """
    Plot and save the data in the given DataFrame.

    Args:
        df (DataFrame): Data to plot.
        title (str): Plot title.
        legend_title (str): Legend title.
        ylabel (str): Y-axis label.
        filename (str): File name to save the plot.
    """
    df.plot(kind="line")
    plt.xlabel("Time")
    plt.ylabel(ylabel)
    plt.title(title)
    plt.legend(title=legend_title)

    # Ensure the directory exists
    os.makedirs(path / "simulation_analysis", exist_ok=True)

    # Save the figure
    plt.savefig(path / f"simulation_analysis/{filename}")
    plt.close()


def plot_agent_decisions(data, output_directory, filename="agent_decisions.png"):
    # Ensure the directory exists
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Define the color palette
    event_types = data["event"].nunique()
    colors = sns.color_palette("dark", event_types)

    # Create a dictionary to map event names to colors
    color_dict = {event: color for event, color in zip(data["event"].unique(), colors)}

    # Create a pivot table
    pivot_data = data.groupby(["agent", "event"]).size().unstack().fillna(0)

    # Create a stacked bar plot for all events excluding 'EXECUTING'
    columns_to_include = ["TALK", "CHOOSE_DESTINATION", "MESSAGE"]
    other_events = pivot_data[
        [col for col in columns_to_include if col in pivot_data.columns]
    ]
    ax = other_events.plot(
        kind="bar",
        stacked=True,
        figsize=(10, 6),
        color=[color_dict[event] for event in other_events.columns],
        width=0.3,
    )

    # Overlay the bars for 'EXECUTING'
    pivot_data["EXECUTING"].plot(
        kind="bar", color=color_dict["EXECUTING"], ax=ax, position=0, width=0.3
    )

    # Add titles, labels, and legend
    plt.title("Number of Events Performed by Each Agent")
    ax.legend(
        title="Event"
    )  # Manually set the legend to ensure all bars are represented
    plt.xlabel("Agent")
    plt.ylabel("Number of Events")
    plt.xticks(rotation=45)  # Rotate agent names for better visibility
    plt.tight_layout()

    # Save the plot
    plt.savefig(os.path.join(output_directory, filename))
    plt.close()


def plot_agent_events(data, output_directory, filename="agent_events_plot.png"):
    # Ensure the directory exists
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Group by agent and event, then count the occurrences
    grouped_data = data.groupby(["agent", "event"]).size().reset_index(name="counts")

    # Create a grouped bar plot using seaborn
    plt.figure(figsize=(15, 7))
    sns.barplot(data=grouped_data, x="agent", y="counts", hue="event", palette="dark")

    # Add titles, labels, and legend
    plt.title("Number of Each Event Type Performed by Each Agent")
    plt.xlabel("Agent")
    plt.ylabel("Number of Events")
    plt.xticks(rotation=45)  # Rotate agent names for better visibility
    plt.legend(title="Event Type", bbox_to_anchor=(1.05, 1), loc="upper left")

    # Save the plot
    plt.tight_layout()
    plt.savefig(os.path.join(output_directory, filename))
    plt.close()


###CONVERSATION ANALYSIS###


def conversation_analysis(path, **kwargs):
    """
    Perform conversation analysis on the conversation data. It calculates metrics,
    creates plots for distributions and histograms of various features.

    Args:
        conv_df (DataFrame): Conversation data frame which contains messages.
    """
    # Calculate or read metrics
    metrics_df = get_or_calculate_metrics(path)

    # Ensure the directory exists
    output_dir = path / "transformer_analysis"
    os.makedirs(output_dir, exist_ok=True)

    # Define the metric lists and corresponding names for distribution plots
    dist_metrics = [("Emotions", EMOTIONS), ("Topics", TOPICS)]
    for metric_name, metric_list in dist_metrics:
        plot_distribution(metrics_df[metric_list], metric_name, output_dir)

    # Define the metric lists and corresponding names for histogram plots
    hist_metrics = [
        ("Toxicity", TOXICITY),
        ("Sentiment", SENTIMENT),
        ("Irony", IRONY),
        ("Coherence", COHERENCE),
    ]
    for metric_name, metric_list in hist_metrics:
        plot_histogram(metrics_df, metric_list, metric_name, output_dir)


def get_or_calculate_metrics(path):
    """
    Calculate or read transformer metrics.

    Args:
        conv_df (DataFrame): Conversation data frame which contains messages.

    Returns:
        DataFrame: DataFrame containing the metrics.
    """
    metrics_file = path / "metrics.csv"
    if metrics_file.is_file():
        metrics_df = pd.read_csv(metrics_file)
    else:
        conv_df = pd.read_csv(path / "conversation.csv")
        print(
            "WARNING - if you want to use this functionality -> uncomment the line below and uncomment the import statement"
        )
        print(
            "This is being done to speed up initializing this file, as the import statement downloads ~ 10 Huggingface models"
        )
        # metrics_df = transformer_metrics.calculate_metrics(list(conv_df['message']))
        metrics_df.to_csv(metrics_file, index=False)
    return metrics_df


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
    counts.columns = ["Submetric", "Count"]

    # Create a figure and axes
    plt.figure(figsize=(10, 6))

    # Create the plot
    sns.barplot(x="Count", y="Submetric", data=counts, palette="viridis")

    # Customize the plot
    plt.title(f"Distribution of Max {metric_name}", fontsize=16)
    plt.xlabel("Count", fontsize=13)
    plt.ylabel(metric_name, fontsize=13)
    plt.xticks(fontsize=11)
    plt.yticks(fontsize=11)

    # Save the figure
    plt.savefig(
        Path(output_dir) / f"{metric_name}_distribution.png",
        bbox_inches="tight",
        dpi=300,
        transparent=False,
    )

    # Close the plot
    plt.close()

    # Create a pie chart
    patches, texts, autotexts = plt.pie(
        counts["Count"], autopct="%1.1f%%", pctdistance=0.85
    )
    plt.axis("equal")  # Equal aspect ratio ensures the pie chart is circular.

    # Increase the size of the labels to make them more visible
    for text in texts:
        text.set_size(12)
    for autotext in autotexts:
        autotext.set_size(10)

    # Add a legend
    plt.legend(patches, counts["Submetric"], loc="best")

    # Save the figure with a transparent background
    plt.savefig(Path(output_dir) / f"{metric_name}_pie_chart.png", transparent=False)

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
    plt.title(f"Distribution of {metric_name}", fontsize=16)
    plt.xlabel("Values", fontsize=13)
    plt.ylabel("Frequency", fontsize=13)
    plt.legend(loc="upper right")
    plt.xticks(fontsize=11)
    plt.yticks(fontsize=11)

    # Save the figure
    plt.savefig(
        Path(output_dir) / f"{metric_name}_histogram.png", bbox_inches="tight", dpi=300
    )

    # Close the plot
    plt.close()


def conversation_repetition_analysis(path, **kwargs):
    df = pd.read_csv(path / "conversation.csv")
    output_dir = path / "conversation_repetition_analysis"
    os.makedirs(output_dir, exist_ok=True)

    # Encode memories to embeddings
    embeddings = SIMILARITY_MODEL.encode(list(df["message"]), convert_to_tensor=True)

    # Analyze memories in the embedding space
    analyze_text_in_embedding_space(
        embeddings, list(df["message"]), "conversation", output_dir
    )


###AGENT MEMORY ANALYSIS###


def agent_memory_analysis(agent, path, **kwargs):
    """
    Perform agent memory analysis on the agent memory data. It calculates and visualizes similarity matrices,
    does hierarchical clustering, and does dimensionality reduction for visualization.

    """
    # Load agent memory data
    memory_data = load_agent_memory_data(agent, path)

    # Ensure the directory exists
    output_dir = path / "memory_analysis"
    os.makedirs(output_dir, exist_ok=True)

    # Save memory data for the selected agent
    save_memory_data(memory_data, output_dir, agent)

    # Initialize dimensionality reduction technique
    dim_reducer = PCA(n_components=2)

    # Initialize placeholders for storing all embeddings, labels, and index ranges
    all_embeddings, index_ranges, start_index = [], {}, 0

    # Process each memory type
    for memory_type, memories in memory_data.items():
        # Skip empty memories
        if len(memories) < 2:
            continue

        # Encode memories to embeddings
        embeddings = SIMILARITY_MODEL.encode(memories, convert_to_tensor=True)

        # Analyze memories in the embedding space
        analyze_text_in_embedding_space(embeddings, memories, memory_type, output_dir)

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


def load_agent_memory_data(agent, path):
    """
    Load agent memory data from a JSON file.

    Returns:
        dict: Loaded agent memory data.
    """
    with open(path / "agent_memory.json", "r") as file:
        data = json.load(file)
    agent = data[agent]
    memory_data = {
        "workmem": [s.split(": ", 1)[-1] if ": " in s else s for s in agent["workmem"]],
        "recentmem": [
            s.split(": ", 1)[-1] if ": " in s else s for s in agent["recentmem"]
        ],
        "convomem": [
            s.split(": ", 1)[-1] if ": " in s else s for s in agent["convomem"]
        ],
        "longmem": [s.split(": ", 1)[-1] if ": " in s else s for s in agent["longmem"]],
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
    with open(output_dir / f"{agent_name}_memories.json", "w") as file:
        json.dump(memory_data, file, indent=4)


def analyze_text_in_embedding_space(embeddings, memories, memory_type, output_dir):
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
        grouped_memories.append(
            [item for item, m in zip(memories, cluster_labels == label) if m]
        )

    with open(output_dir / f"{memory_type}_groups.json", "w") as file:
        json.dump(grouped_memories, file, indent=4)


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
    sns.heatmap(similarity_scores, annot=False, square=True)
    plt.savefig(f"{output_dir}/{memory_type}_heatmap.png")
    plt.close()

    # Create a clustermap
    cmap = sns.diverging_palette(230, 20, as_cmap=True)
    g = sns.clustermap(
        similarity_scores,
        cmap=cmap,
        vmax=1,
        vmin=-1,
        center=0,
        linewidths=0.5,
        cbar_kws={"shrink": 0.5},
    )
    g.fig.savefig(f"{output_dir}/{memory_type}_clustermap.png")
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
    cmaps = ["Blues", "Reds", "Greens", "Purples", "Greys"]
    patches = []

    # Generate masked heatmap for each memory type and colormap
    for (label, (start, end)), cmap in zip(index_ranges.items(), cmaps):
        mask = np.triu(np.ones_like(similarity_matrix, dtype=bool))
        mask[start:end, start:end] = False
        sns.heatmap(
            similarity_matrix, mask=mask, cmap=cmap, cbar=False, center=0.0, square=True
        )
        patches.append(mpatches.Patch(color=sns.color_palette(cmap)[2], label=label))

    # Final heatmap for the upper triangle
    mask = np.triu(np.ones_like(similarity_matrix, dtype=bool))
    sns.heatmap(
        similarity_matrix,
        mask=mask,
        square=True,
        cmap="Oranges",
        linewidths=0.7,
        cbar_kws={"shrink": 0.5},
    )

    # Add legend and save the heatmap
    plt.legend(handles=patches, bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.0)
    plt.savefig(f"{output_dir}/combined_heatmap.png")
    plt.close()

    # Generate and save the clustermap
    cmap = sns.diverging_palette(230, 20, as_cmap=True)
    clustermap = sns.clustermap(
        similarity_matrix,
        cmap=cmap,
        vmax=1,
        vmin=-1,
        center=0,
        linewidths=0.5,
        cbar_kws={"shrink": 0.5},
    )
    plt.title("Visualization for All Memories")
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
    dist = pdist(embeddings, metric="cosine")

    # Create a linkage matrix
    linkage_matrix = linkage(dist, "ward")

    # Create a figure
    fig = plt.figure(figsize=(8, 8))

    # Plot the dendrogram
    dendro = dendrogram(linkage_matrix)
    plt.savefig(f"{output_dir}/{memory_type}_dendrogram.png")
    plt.close()

    # Find an optimal 't' that results in a desirable number of clusters (between 2 and 5)
    t_values = np.linspace(
        0, 5, num=11
    )  # You might want to adjust the range and step size
    for t in t_values:
        cluster_labels = fcluster(linkage_matrix, t, criterion="distance")
        if 2 <= len(set(cluster_labels)) <= 5:
            break

    return cluster_labels


def plot_reduced_embeddings(embeddings, memory_type, output_dir):
    # Convert to DataFrame for easier plotting
    df = pd.DataFrame(embeddings, columns=["x", "y"])

    # Create a scatter plot
    plt.figure(figsize=(6, 6))

    # Create a sequence array based on the order of the memories
    sequence = np.arange(len(df))

    # Plot the scatter points with colors based on the sequence
    scatter = plt.scatter(df["x"], df["y"], c=sequence, cmap="viridis")
    plt.title(f"Visualization for {memory_type}")

    # Add a colorbar
    colorbar = plt.colorbar(scatter)
    colorbar.set_label("Progress of Memories")

    # Save the plot
    plt.savefig(f"{output_dir}/{memory_type}_scatter.png")
    plt.close()
