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

def get_memories(agent, question):
    output = {}
    longmem_responses = agent.memory.query(
        memory_key="longmem",
        text=question,
        num_memories_queried=2,
    )
    output["longmem"] = "\n".join(longmem_responses)
    recentmem_responses = agent.memory.query(
        memory_key="recentmem",
        text=question,
        num_memories_queried=1,
    )
    output["recentmem"] = "\n".join(recentmem_responses)
    return output

def talk_chain(question, agent, llm, chain_input):
    chain_input.update(get_memories(agent, question))

    chain_input["action_name"] = "talk"
    chain_input["action_goal"] = "respond to the interviewer as best I can"
    chain_input["convomem"] = f"The interviewer said: {question}"
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
    return response

def memory_update(agent, talk_item: str, chain_input):
    agent.memory.add(content={"talk": talk_item}, data_collector = [])
    agent.memory.update(new_summary={"summary": chain_input["summary"]}, no_summary=False)

def summary_update(agent, question, response, llm, chain_input):
    chain_input.update(get_memories(agent, response))
    chain_input["current_goal"] = agent.current_goal
    chain_input["location"] = "in an interview area"
    chain_input["question"] = question
    chain_input["response"] = response

    template = """Suppose you ARE the person, {name}, described below.
        \nThe following summarizes what is going on right now: {summary}
        \nYour state of mind: {current_goal}
        \n
        \nYour task is to update the summary in character, using recent observations and relevant memories, delimited by triple brackets below.
        \nYou remember: ```\n{recentmem}\n{longmem}```\n
        \nYou are currently {location}.
        \nYou just observed: ```\n{question}\n{response}```\n
        \nIntegrate your state of mind into the summary and emphasize information that is relevant to the state of mind and minimize those that are not.
        \nThe summary should include thoughts and summarize conversations you are having. Use first person perspective. Maintain a cohesive summary with fewer than 100 words: [SUMMARY]
        """
    prompt = PromptTemplate.from_template(template)

    chain = LLMChain(prompt=prompt, llm=llm, verbose=True)
    response = chain.run(chain_input)
    # parser_config:
    #     summary: "[SUMMARY]"
    return response

# Evaluation function
def reflect_interview(questions, results_dict, agent, llm, **kwargs):
    print("\nRUNNING REFLECT RESPONSE FUNCTION")
    """Check if agent's response is correct."""
    # if not results_dict:
    #     results_dict = {"success": 0, "failure": 0, "total": 0}

    chain_input = {}

    initial_question = questions[0]
    chain_input["summary"] = summarizer(initial_question, agent, llm)

    for i, question in enumerate(questions):
        response = talk_chain(question, agent, llm, chain_input)
        response = f"I said: {response}"
        results_dict[f"response {i+1}"] = response

        memory_update(agent, response, chain_input)

        if i < len(questions)-1:
            chain_input["summary"] = summary_update(agent, f"the interviewer said: {question}", response, llm, chain_input)

    return results_dict
