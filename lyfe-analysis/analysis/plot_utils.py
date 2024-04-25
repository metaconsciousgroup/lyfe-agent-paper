import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx
import numpy as np
import os
from pathlib import Path

FIGUREPATH = Path(os.path.realpath(__file__)).parent.parent / 'figures'

PNAME_DICT = {
    'len_conv': 'Conversation Length',
    'hobbies': 'Hobbies',
    'pets': 'Pets',
    'genders': 'Gender',
}


def pname(original_name: str) -> str:
    """Pretty/Paper/Publication name."""
    # Get value in PNAME_DICT, if key doesn't exist, return original name
    return PNAME_DICT.get(original_name, original_name)


def plot_distribution(df, column_A, column_B=None, save_fig=False):
    """Plot distribution of column_A values, conditioned on column_B unique values

    """
    # Set the style and color palette
    sns.set(style='whitegrid')

    if column_B is None:
        sns.histplot(data=df, x=column_A, weights=1 / len(df), bins=10,
                     kde=True, alpha=0.5, edgecolor='black', linewidth=1)
        title = f"Distribution of {pname(column_A)}"
    else:
        palette = sns.color_palette("husl", len(df[column_B].unique()))
        # Create a histogram for each unique value in column B
        for idx, value in enumerate(df[column_B].unique()):
            sns.histplot(data=df[df[column_B] == value], x=column_A,
                         weights=1 / len(df), bins=10, kde=False,
                         label=value, color=palette[idx], alpha=0.5, edgecolor='black', linewidth=1)
        title = f"Distribution of {pname(column_A)} based on {pname(column_B)}"

    # Add title, labels, legend and show/save the plot
    plt.title(title)
    plt.xlabel(pname(column_A))
    plt.ylabel('Proportion')
    if column_B is not None:
        plt.legend(title=pname(column_B))

    if save_fig:
        if column_B is None:
            plt.savefig(FIGUREPATH / f"{column_A}_distribution.png")
        else:
            plt.savefig(FIGUREPATH / f"{column_A}_vs_{column_B}_distribution.png")
    else:
        plt.show()

    plt.close()


def plot_groupby(df, columns_to_group=None, column_values=None):
    """
    Plot values conditioned on different columns values
    """
    # Set the style and color palette
    sns.set(style='whitegrid')

    grouped_df = df.groupby(columns_to_group)[column_values].agg(['mean', 'std', 'count']).reset_index()

    # Calculate standard error
    grouped_df['stderr'] = grouped_df['std'] / grouped_df['count'] ** 0.5

    new_col = ''
    for i, x in enumerate(columns_to_group):
        if i != len(columns_to_group) - 1:
            new_col += grouped_df[x] + ' - '
        else:
            new_col += grouped_df[x]
    grouped_df['combined'] = new_col
    grouped_df = grouped_df.sort_values('mean', ascending=True)

    # Plot the data using seaborn barplot
    plt.figure(figsize=(15, 10))
    sns.barplot(data=grouped_df, x='combined', y='mean', yerr=grouped_df['stderr'], capsize=0.1)
    plt.xlabel('Combinations')
    plt.ylabel(f'Mean {column_values}')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(FIGUREPATH / f"groupby.png", dpi=300, bbox_inches='tight')
    plt.close()


def person_info(df, first_name, last_name):
    row = df.loc[(df['agent1_first_name'] == first_name) & (df['agent1_last_name'] == last_name)].iloc[0]
    return f"{first_name} {last_name}, {row['agent1_gender']}, {row['agent1_age']}, {row['agent1_occupation']}, {row['agent1_personality']}, {row['agent1_hobby']}, {row['agent1_pet']}"


def mean_len_conv(df, person1_first, person1_last, person2_first, person2_last):
    # Filter rows where either person1 or person2 are involved
    filtered = df[(df['agent1_first_name'] == person1_first) & (df['agent1_last_name'] == person1_last) | (
            df['agent2_first_name'] == person2_first) & (df['agent2_last_name'] == person2_last)]
    return filtered['len_conv'].mean()


def connection_graph(df):
    G = nx.Graph()

    for index, row in df.iterrows():
        person1 = f"{row['agent1_first_name']} {row['agent1_last_name']}"
        person2 = f"{row['agent2_first_name']} {row['agent2_last_name']}"

        G.add_node(person1)
        G.add_node(person2)

        mean_conv = mean_len_conv(df, row['agent1_first_name'], row['agent1_last_name'], row['agent2_first_name'],
                                  row['agent2_last_name'])
        G.add_edge(person1, person2, weight=mean_conv)

        # Use a colormap to map edge weights to colors
        cmap = plt.cm.viridis
        weights = [e[2]['weight'] for e in G.edges(data=True)]
        min_weight = min(weights)
        max_weight = max(weights)
        norm = plt.Normalize(min_weight, max_weight)

        # Create a dictionary mapping edges to colors based on weight
        edge_colors = {e[:2]: cmap(norm(e[2]['weight'])) for e in G.edges(data=True)}

        pos = nx.circular_layout(G)

        # Draw nodes and labels
        nx.draw_networkx_nodes(G, pos, node_color='lightgreen', node_size=250)
        nx.draw_networkx_labels(G, pos, labels={n: n for n in G.nodes()}, font_size=5, font_weight='bold')

        # Draw edges with colors mapped from the colormap
        for edge, color in edge_colors.items():
            nx.draw_networkx_edges(G, pos, edgelist=[edge], edge_color=color, alpha=0.75)

        plt.axis('off')
        plt.savefig(FIGUREPATH / f"connection_graph.png", dpi=300, bbox_inches='tight')
        plt.close()

        # top_edges = sorted(G.edges(data=True), key=lambda x: x[2]['weight'], reverse=True)[:3]
        # top_edges = [(e[0], e[1], e[2]['weight']) for e in top_edges]

        # def edge_color(edge):
        #     edge_pairs = [(e[0], e[1]) for e in top_edges]  # Extract only the node pairs from top_edges
        #     if edge in edge_pairs or (edge[1], edge[0]) in edge_pairs:
        #         return 'red'
        #     else:
        #         return 'blue'

        # edge_colors = [edge_color(edge) for edge in G.edges()]
        # pos = nx.circular_layout(G)

        # # Draw nodes and labels
        # nx.draw_networkx_nodes(G, pos, node_color='lightgreen', node_size=250)
        # nx.draw_networkx_labels(G, pos, labels={n: n for n in G.nodes()}, font_size=5, font_weight='bold')

        # # Draw edges with different colors and alpha values
        # for edge, color in zip(G.edges(), edge_colors):
        #     alpha = 0.35 if color == 'blue' else 1
        #     nx.draw_networkx_edges(G, pos, edgelist=[edge], edge_color=color, alpha=alpha)

        # # Draw edge labels
        # edge_labels = {(e[0], e[1]): f"{e[2]:.2f}" for e in top_edges}
        # nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=5, font_weight='bold', label_pos=0.5)

        # # Display information for the strongest connections
        # connection_info = '\n'.join([f"{person_info(df, e[0].split()[0], e[0].split()[1])} - {person_info(df, e[1].split()[0], e[1].split()[1])}" for e in top_edges])
        # plt.text(0.5, -0.1, connection_info, horizontalalignment='center', verticalalignment='center', transform=plt.gca().transAxes, fontsize=10, bbox=dict(facecolor='none', edgecolor='black', boxstyle='round,pad=1'))

        # plt.axis('off')
        # plt.savefig(FIGUREPATH / f"connection_graph.png", dpi=300, bbox_inches='tight')
        # plt.close()