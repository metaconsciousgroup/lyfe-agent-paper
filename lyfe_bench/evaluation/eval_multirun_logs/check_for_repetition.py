import numpy as np
import pandas as pd

from langchain import LLMChain, PromptTemplate

from sklearn.metrics.pairwise import cosine_similarity


def check_for_repetition(results_dict, cwdir, window_size,llm, **kwargs) -> dict:
    """
    Check if a specific agent has mentioned some information in the conversation by using a large language model.

    Parameters
    ----------
    results_dict: dict
        A dictionary to keep track of the results. 
    agent_name : str
        The name of the agent.
    info_to_check : str
        The information that the agent is supposed to mention.
    df : pd.DataFrame
        The dataframe containing the conversation history.
    llm: object
        Large Language Model that will evaluate the agent's message.
        
    Returns
    -------
    bool
        True if the agent mentioned the information, False otherwise.
    """

    df = pd.read_csv(cwdir / 'conversation.csv', index_col=0)

    agent_names = df['sender'].unique()


    if not results_dict:
        results_dict = {agent : {"repetitiveness" : 0, "total" : 0} for agent in agent_names}

    #Extract the messages of each agent
    for agent in agent_names:
        agent_messages = df[df['sender'] == agent]['message']

        for i in range(len(agent_messages) - window_size + 1):
            window = agent_messages[i:i+window_size].str.cat(sep='\n-')

            template = f"""
            Conider the following messages: \n-{window}
            Determine whether the messages are repetitive.
            Your answer should be a one-word response, YES or NO.
            """

            prompt = PromptTemplate.from_template(template)
            # Instantiate the interviewer with the LLM and prompt
            interviewer = LLMChain(prompt=prompt, llm=llm, verbose=True)
            # Run the interviewer with the context and information to check
            evaluation = interviewer.run({'window': window})
            print('evaluation:', evaluation)

            # evaluation = evaluation.split('.')[0]
            results_dict[agent]['total'] += 1

            if evaluation.lower() == 'yes':
                results_dict[agent]['repetitiveness'] += 1

    return results_dict