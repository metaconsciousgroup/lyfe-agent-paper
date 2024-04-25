import numpy as np

from langchain import LLMChain, PromptTemplate

from sklearn.metrics.pairwise import cosine_similarity
from lyfe_agent.encoder_utils import SentenceTransformerEncoder # TODO: make config

def check_memory(results_dict, agent, desired_content, llm, k=5, **kwargs):
    print("\nRUNNING CHECK MEMORY FUNCTION")
    """
    Check if agent memories contains desired content
    """
    # TODO: make encoder choice configurable
    encoder = SentenceTransformerEncoder('all-MiniLM-L12-v2')

    for memory_key in agent.memory.memory_keys:
        # get memory content from current module
        memory_module = getattr(agent.memory, memory_key)
        # eval dictinary setup
        results_dict[memory_key] = results_dict.get(memory_key, {'success': 0, 'failure': 0, 'total': 0})

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
        print('evaluation:', evaluation)
        # update results
        results_dict[memory_key]['total'] += 1
        if evaluation.lower() == 'yes':
            results_dict[memory_key]['success'] += 1
        else:
            results_dict[memory_key]['failure'] += 1

    return results_dict
