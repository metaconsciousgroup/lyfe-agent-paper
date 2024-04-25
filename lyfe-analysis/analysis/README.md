# Analysis Directory

This directory contains the scripts and outputs for various types of analyses conducted on the data. The primary script for conducting these analyses is `run_analysis.py`.

## Running the Analysis Script

You can run the script with the following command:

python run_analysis.py --path ./multirun/2023-07-12/14-52-30/0/ --agent "Fatima Al-Sayed"

Optional arguments include:
--agent AGENT_NAME Specify the agent name to perform agent-memory analysis.


## Output

The outputs of each function are plots saved as images in the specified subdirectories within the experiment directory. Each function creates a directory corresponding to its name under `multirun/[date]/[time]/0/` and saves its output plots there.

1. `simulation_analysis/` has the simulation events plotted over time

2. `transformer_analysis/` has the agents' textual responses plotted against each transformer model. refer to `transformer_metrics.py` for a full list of analysis

3. `memory_analysis/` takes 1 agent and analyzes their different memory components. Concretely, it embeds their memories using a model from `sentence_transformers` and measures the cosine similarity between all the embeddings. The results can be visualized with a heatmap, clustermap, dendogram, or plotted after dimensionality reduction.
   
    a.  the heatmap maintains the ordering of the memories

    b. the clustermap groups those memories most similar close to each other
   
    c. the dendogram shows the same thing as the clustermap in a different format
   
    d. the groups JSON shows what these clusters could be. THIS REQUIRES EXTRA WORK


## Description of Analysis Script

`run_analysis.py` contains several functions that conduct different types of analyses:

1. `temporal_analysis(log_df)`: This function analyzes temporal patterns in the logs. The output plots are saved in the `simulation_analysis` directory.

2. `conversation_analysis(conv_df)`: This function analyzes conversations by passing each agent response to various transformer models. The output plots are saved in the `transformer_analysis` directory.

3. `agent_memory_analysis()`: This function performs an analysis of agent memory. The output plots are saved in the `memory_analysis` directory. This function is run only if the `--agent` argument is specified when running the script.

The script also includes several plotting functions. These take in data, perform some form of analysis or plotting, and then save the resulting plot in the corresponding directory. These functions are:

1. `plot_distribution(df, metric_name, output_dir)`: Plots a distribution of a specified metric and saves the plot to the specified directory.

2. `plot_histogram(metrics_df, metric_list, metric_name, output_dir)`: Plots a histogram of specified metrics and saves the plot to the specified directory.

3. `plot_similarity_matrices(similarity_scores, memory_type, output_dir)`: Plots similarity matrices for a given memory type and saves the plots to the specified directory.

4. `plot_combined_similarity_matrices(similarity_scores, memory_type, output_dir)`: Plots similarity matrices for all memory types and saves the plots to the specified directory.

5. `plot_hierarchical_clustering(embeddings, memory_type, output_dir)`: Plots a hierarchical clustering dendrogram based on embeddings for a given memory type and saves the plot to the specified directory.

6. `plot_reduced_embeddings(embeddings, memory_type, output_dir)`: Plots reduced dimensionality embeddings for a given memory type and saves the plot to the specified directory.


## A note on transformers_metrics.py

This is a highly modifiable file that will allow you to plug-and-play with bascally any model from Huggingface. If there is a model that you would like to include, just make a new variable for it and initialize it in the same way as the other models. Pay attention to the task of the model, as that modifies how it is initialized and implemented.

