from copy import deepcopy
from langchain import LLMChain, PromptTemplate


def summarizer(
    initial_question, agent, llm
):  # initial_question, template, agent, llm):
    template = """Suppose you ARE the person, {name}, described below.
    \nYou will be asked to make several choices in character, as the person you are assumed to be.\n
    \nYou are asked the following question: {initial_question}
    \nCome up with a summary using the following memories that attempt to address this question: ```\n{longmem}\n```
    \nYour ({name}) summary here: 
    """
    prompt = PromptTemplate.from_template(template)
    longmem_responses = agent.memory.query(
        memory_key="longmem",
        text=initial_question,
        num_memories_queried=15,
    )
    longmem = "\n".join(longmem_responses)
    # recentmem_responses = agent.memory.query(
    #     memory_key="recentmem",
    #     text=initial_question,
    #     num_memories_queried=5,
    # )
    # recentmem = "\n".join(recentmem_responses)

    chain_input = {
        "longmem": longmem,
        "name": agent.name,
        "initial_question": initial_question,
    }
    reflection = LLMChain(prompt=prompt, llm=llm, verbose=True)
    summary = reflection.run(chain_input)
    return summary


def no_summary_reflect_response(initial_question, results_dict, agent, llm, **kwargs):
    print("\nRUNNING REFLECT RESPONSE FUNCTION")
    """Check if agent's response is correct."""
    # if not results_dict:
    #     results_dict = {"success": 0, "failure": 0, "total": 0}

    chain_input = {}

    chain_input["summary"] = summarizer(initial_question, agent, llm)

    if id(agent.memory.longmem) == id(agent.memory.recentmem):
        responses = agent.memory.query(
            memory_key="longmem",
            text=initial_question,
            num_memories_queried=3,
        )
        longmem_responses = responses[:2]
        chain_input["longmem"] = "\n".join(longmem_responses)
        recentmem_responses = responses[2:]
        chain_input["recentmem"] = "\n".join(recentmem_responses)
    else:
        longmem_responses = agent.memory.query(
            memory_key="longmem",
            text=initial_question,
            num_memories_queried=2,
        )
        chain_input["longmem"] = "\n".join(longmem_responses)
        recentmem_responses = agent.memory.query(
            memory_key="recentmem",
            text=initial_question,
            num_memories_queried=1,
        )
        chain_input["recentmem"] = "\n".join(recentmem_responses)

    chain_input["action_name"] = "talk"
    chain_input["action_goal"] = "respond to the interviewer as best I can"
    chain_input["convomem"] = f"The interview said: {initial_question}"
    chain_input["name"] = agent.name
    chain_input["nearby_creature"] = "the interviewer"
    chain_input["current_goal"] = "Respond to the interview question as best I can"
    chain_input["location"] = "at an interview location"
 
    template = """Suppose you ARE the person, {name}, described below.
        \nYou will be asked to make several choices in character, as the person you are assumed to be.\n
        \nYour state of mind: {current_goal}
        \nYou are currently {location}.
        \nYou remember that: \n```\n{recentmem}\n{longmem}\n```\n
        \nYou choose to talk for the following reason: '{action_goal}'.\n
        \nYou are to write a reply to the following conversation. Your reply should be short and in character. Your reply can only be heard by {nearby_creature}.
        \nHere is a sequence of memories for the most recent conversation you ({name}) had: \n{convomem}
        \nYou ({name}) should respond to the latest conversation, sticking with your reason for speaking, by saying: [YOUR REPLY]
        """

    prompt = PromptTemplate.from_template(template)

    talk_chain = LLMChain(prompt=prompt, llm=llm, verbose=True)
    response = talk_chain.run(chain_input)
    results_dict["response"] = response
    return results_dict


# Evaluation function
def reflect_response(initial_question, results_dict, agent, llm, use_summary=True, **kwargs):
    if not use_summary:
        return no_summary_reflect_response(initial_question, results_dict, agent, llm, **kwargs)
    print("\nRUNNING REFLECT RESPONSE FUNCTION")
    """Check if agent's response is correct."""
    # if not results_dict:
    #     results_dict = {"success": 0, "failure": 0, "total": 0}

    chain_input = {}

    chain_input["summary"] = summarizer(initial_question, agent, llm)

    if id(agent.memory.longmem) == id(agent.memory.recentmem):
        responses = agent.memory.query(
            memory_key="longmem",
            text=initial_question,
            num_memories_queried=3,
        )
        longmem_responses = responses[:2]
        chain_input["longmem"] = "\n".join(longmem_responses)
        recentmem_responses = responses[2:]
        chain_input["recentmem"] = "\n".join(recentmem_responses)
    else:
        longmem_responses = agent.memory.query(
            memory_key="longmem",
            text=initial_question,
            num_memories_queried=2,
        )
        chain_input["longmem"] = "\n".join(longmem_responses)
        recentmem_responses = agent.memory.query(
            memory_key="recentmem",
            text=initial_question,
            num_memories_queried=1,
        )
        chain_input["recentmem"] = "\n".join(recentmem_responses)

    chain_input["action_name"] = "talk"
    chain_input["action_goal"] = "respond to the interviewer as best I can"
    chain_input["convomem"] = f"The interview said: {initial_question}"
    chain_input["name"] = agent.name
    chain_input["nearby_creature"] = "the interviewer"

    template = """Suppose you ARE the person, {name}, described below.
        \nYou will be asked to make several choices in character, as the person you are assumed to be.\n
        \nThe following summary describes what is currently going on:\n{summary}\n
        \nYou remember that: \n```\n{recentmem}\n{longmem}\n```\n
        \nYou choose to {action_name} for the following reason: '{action_goal}'.\n
        \nYou are to write a reply to the following conversation. Your reply should be short and in character. Your reply can only be heard by {nearby_creature}.
        \nHere is a sequence of memories for the most recent conversation you ({name}) had: \n{convomem}
        \nYou ({name}) should respond to the latest conversation by saying: [YOUR REPLY]
        """
    prompt = PromptTemplate.from_template(template)

    talk_chain = LLMChain(prompt=prompt, llm=llm, verbose=True)
    response = talk_chain.run(chain_input)
    results_dict["response"] = response
    return results_dict
