import pandas as pd


from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import json
import seaborn as sns
import matplotlib.pyplot as plt

def visualize_results(results):
    for memory_type, data in results.items():
        # Extract pairwise similarities
        similarities = data["Pairwise Similarities"]
        
        # Prepare data for heatmap
        heatmap_data = []
        run_labels = sorted(set(run for pair in similarities.keys() for run in pair.split(" - ")))
        for run_i in run_labels:
            row = []
            for run_j in run_labels:
                if run_i == run_j:
                    row.append(1)  # max similarity with itself
                else:
                    pair = " - ".join(sorted([run_i, run_j]))
                    row.append(similarities.get(pair, 0))  # 0 if pair not found (shouldn't happen)
            heatmap_data.append(row)
        
        # Plot heatmap
        plt.figure(figsize=(10, 8))
        sns.heatmap(heatmap_data, annot=True, cmap="YlGnBu", xticklabels=run_labels, yticklabels=run_labels)
        plt.title(f"Similarities between runs for {memory_type}")
        plt.show()


def compare_runs(memory_dict):
    model = SentenceTransformer('all-MiniLM-L6-v2')

    results = {}

    # For each type of memory
    for memory_type, runs in memory_dict.items():
        avg_similarities = []
        pair_similarities = {}

        # Get a list of all sentences from all runs
        all_sentences = [sentence for run in runs.values() for sentence in run]
        # Compute embeddings for all sentences
        all_embeddings = model.encode(all_sentences)

        # For each pair of runs
        for i in range(len(runs)):
            for j in range(i + 1, len(runs)):
                # Compute embeddings for sentences in each run
                run_i_embeddings = all_embeddings[int(i) * len(runs[str(i)]) : (int(i) + 1) * len(runs[str(i)])]
                run_j_embeddings = all_embeddings[int(j) * len(runs[str(j)]) : (int(j) + 1) * len(runs[str(j)])]

                # Compute cosine similarities between all pairs of sentences in the two runs
                cos_sim = cosine_similarity(run_i_embeddings, run_j_embeddings)

                # Take the max similarity for each sentence in run i
                max_similarities = np.max(cos_sim, axis=1)

                # Compute average max similarity for this pair of runs
                avg_max_similarity = np.mean(max_similarities)
                avg_similarities.append(avg_max_similarity)

                pair_similarities[f"Run {i} - Run {j}"] = avg_max_similarity

        # Compute average similarity for this type of memory
        avg_similarity = np.mean(avg_similarities)

        results[memory_type] = {
            "Average Similarity": avg_similarity,
            "Pairwise Similarities": pair_similarities,
        }

    return results


def check_convergence(agent_memories):
    """TODO: Docstring for check_convergence."""

    for memory_key in agent.memory.memory_keys:
        # get memory content from current module
        memory_module = getattr(agent.memory, memory_key)
        # eval dictinary setup
        results_dict[memory_key] = results_dict.get(memory_key, {'success': 0, 'failure': 0, 'total': 0})

        # TODO: make encoder choice configurable
        encoder = SentenceTransformerEncoder('bert-base-nli-mean-tokens')

        # get memory content and embeddings
        memory_content = memory_module.data
        memory_embeddings = encoder(memory_content).reshape(-1, encoder.dim)

        # get top k most similar memories
        query_embedding = encoder(desired_content).reshape(1, encoder.dim)
        cosine_similarities = cosine_similarity(
            query_embedding, memory_embeddings
        )[0]

        # Get top k similar memories
        I = np.argsort(cosine_similarities)[::-1][:k]
        top_memories = '\n-'.join([memory_content[i] for i in I])
 
        # evaluate answer
        template = """Consider the following statement, delimited by triple backticks: ```{desired_content}```
                    Determine whether the information from the previous statement is contained in the following: \n-{top_memories}
                    Your answer should be a one-word response, YES or NO."""
        prompt = PromptTemplate.from_template(template)
        evaluator = LLMChain(prompt=prompt, llm=llm, verbose=True)
        evaluation = evaluator.run(
            {'desired_content': desired_content, 'top_memories': top_memories}
            )
        
        # update results
        results_dict[memory_key]['total'] += 1
        if evaluation.lower() == 'yes':
            results_dict[memory_key]['success'] += 1
        else:
            results_dict[memory_key]['failure'] += 1    


#TODO: Ask Andrew about such an implementation

# It seems like you want to compare the topic distributions from different runs to see if they're becoming more similar over time. There are several methods to compare distributions:

# 1. **Chi-Squared Test**: This test is used to determine if there is a significant association between two categorical variables (in your case, run number and topic proportions). However, it's more useful for comparing observed frequencies to expected frequencies.

# 2. **Kullback-Leibler (KL) Divergence**: KL Divergence measures how one probability distribution diverges from a second expected probability distribution. If the KL divergence is small, the distributions are similar. For this, you would need to set a 'target' distribution to compare each run against, which might be difficult if you expect each run to evolve naturally.

# 3. **Jensen-Shannon Divergence**: This is a symmetric version of KL divergence and might be more suitable if you don't have a 'target' distribution. It measures the average divergence of each distribution from the average of all the distributions. A value close to 0 indicates that the distributions are very similar.

# 4. **Earth Mover's Distance (also known as Wasserstein distance)**: This is another way to measure the distance between two probability distributions. It's intuitive as it can be thought of as the minimum amount of "work" required to transform one distribution into the other.

# 5. **Cosine Similarity**: Cosine similarity measures the cosine of the angle between two vectors. You could treat your distributions as vectors and calculate their cosine similarity. The closer the cosine similarity is to 1, the more similar the distributions are.

# All these methods can be useful for comparing distributions. Note that each has its own assumptions and limitations. You should choose the one that makes the most sense for your specific context. 

# Also, consider visualizing your distributions using plots like bar charts or line plots over runs. Visualizing your data might give you a good qualitative feel for how similar your distributions are getting over time. 

# Lastly, remember that if you're looking at whether runs are converging to be the same, you'd want to look at trends over time (e.g., is the difference between runs decreasing over time?). You might need to use time series analysis techniques to do this.

# Sure, let's delve deeper into time series analysis in your context. The central idea here is to examine how the distance between topic distributions changes over time.

# First, you would need to calculate a 'distance' or 'dissimilarity' measure between the topic distributions for each pair of consecutive runs. You can use any of the methods mentioned above (Chi-Squared, Kullback-Leibler Divergence, Jensen-Shannon Divergence, Earth Mover's Distance, or Cosine Similarity).

# After calculating these distances, you would have a series of values over time that represent how much the topic distribution is changing from one run to the next. This series of values is your time series.

# With this time series, you can:

# 1. **Visualize the data**: Start by plotting the series to get a visual sense of whether the distances are generally increasing, decreasing, or staying the same over time.

# 2. **Look for trends**: You can use statistical techniques like moving averages to identify any underlying trends. If the trend line is decreasing, that would suggest your topic distributions are becoming more similar over time.

# 3. **Apply time series decomposition**: This technique separates a time series into its trend, seasonal, and residual components. The trend component would show whether there's a long-term increase or decrease in the distance measure. 

# 4. **Test for stationarity**: A stationary time series is one whose properties do not depend on the time at which the series is observed. If the time series of your distance measure is stationary, that would suggest your topic distributions aren't systematically changing over time. You can use tests like the Augmented Dickey-Fuller test to check for stationarity.

# 5. **Test for autocorrelation**: Autocorrelation refers to the correlation of a time series with a delayed copy of itself. If the distance measure is correlated with its past values, that would suggest some form of systematic change over time. The Durbin-Watson test is one way to test for autocorrelation.

# Remember, time series analysis is a large field and these are just starting points. The appropriate methods depend heavily on the specifics of your data and what you're hoping to find out.