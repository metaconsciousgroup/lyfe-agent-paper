import numpy as np
import pandas as pd

from lyfe_agent.langmodel import get_api_keys
from langchain import LLMChain, PromptTemplate
from langchain.chat_models import ChatOpenAI
from utils.saveload import load_agent_memory

from sklearn.metrics.pairwise import cosine_similarity
# from lyfe_agent.embedding_utils import SentenceTransformerEncoder # TODO: make config

# ENCODER = SentenceTransformerEncoder('bert-base-nli-mean-tokens')

def check_for_mention(results_dict, agent_name, info_to_mention, cwdir, llm, **kwargs) -> bool:
    print("\nRUNNING CHECK FOR MENTION FUNCTION")
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

    if not results_dict:
        results_dict = {'success': 0, 'failure': 0, 'total': 0}

    # # Extract the messages of the agent
    # agent_messages = df[df['sender'] == agent_name]['message']
    # message_embeddings = ENCODER(agent_messages.tolist()).reshape(-1, ENCODER.dim)

    # # get top k most similar memories
    # query_embedding = ENCODER(info_to_mention).reshape(1, ENCODER.dim)
    # cosine_similarities = cosine_similarity(
    #     query_embedding, message_embeddings
    # )[0]

    # # Get top k similar memories
    # I = np.argsort(cosine_similarities)[::-1][:agent_messages.shape[0]/2]
    # agent_messages = '\n-'.join([agent_messages[i] for i in I])

    # # Extract the messages of the agent
    agent_messages = df[df['sender'] == agent_name]['message'].str.cat(sep='\n-')
    if agent_messages == '':
        agent_messages = 'No messages from lyfe_agent.'
    info = info_to_mention if isinstance(info_to_mention, str) else '\n-'.join(list(info_to_mention))

    if isinstance(info_to_mention, str):
        # Set up evaluation template
        template = """
        Consider the statement, delimited by triple backticks: \n```\n-{info}\n```
        Determine whether this statement is also present in ANY of the following sentences (importantly, wording does NOT have to be the same): \n-{context}
        You should answer YES if the information is contained in any of the sentences, even if the wording is different.
        Your answer should be a one-word response, YES. or NO., followed by a short reason.
        """
    else:
        template = """
        Consider the statements, delimited by triple backticks: \n```\n-{info}\n```
        Determine whether ANY of the previous statements are also present in ANY of the following sentences (importantly, wording does NOT have to be the same): \n-{context}
        You should answer YES if the information is contained in any of the sentences, even if the wording is different.
        Your answer should be a one-word response, YES. or NO., followed by a short reason.
        """

    prompt = PromptTemplate.from_template(template)
    
    # Instantiate the interviewer with the LLM and prompt
    interviewer = LLMChain(prompt=prompt, llm=llm, verbose=True)
    
    # Run the interviewer with the context and information to check
    evaluation = interviewer.run({'context': agent_messages, 'info': info, 'agent_name': agent_name})
    print('evaluation:', evaluation)
    evaluation = evaluation.split('.')[0]
    results_dict['total'] += 1

    if evaluation.lower() == 'yes':
        results_dict['success'] += 1
    else:
        results_dict['failure'] += 1

    return results_dict
    

