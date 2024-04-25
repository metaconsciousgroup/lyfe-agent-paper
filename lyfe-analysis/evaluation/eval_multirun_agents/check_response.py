from copy import deepcopy
from langchain import LLMChain, PromptTemplate


def check_response(results_dict, agent, question, correct_answers, llm, **kwargs):
    print("\nRUNNING CHECK RESPONSE FUNCTION")
    """Check if agent's response is correct."""
    if not results_dict:
        results_dict = {"success": 0, "failure": 0, "total": 0}

    # get interview response
    chain_input = deepcopy(agent.chain_input)

    chain_input.update(
        {"talk": question + " [Only answer the question!]", "time": "00:00", "question" : question}
    )

    agent.memory.add(
        content={"talk": question, "time": "00:00"},
        key="sense",
    )

    answer = agent.chains["talk"].run(chain_input)

    # evaluate answer
    correct_answers = correct_answers if isinstance(correct_answers, str) else '\n-'.join(list(correct_answers))
    template = """Consider the statement, delimited by triple backticks: \n```\n-{answer}\n```
            Determine whether this statement is also present in ANY of the following sentences (importantly, wording does NOT have to be the same): \n-{correct_answers}
            You should answer YES if the information is contained in any of the sentences, even if the wording is different.
            Your answer should be a one-word response, YES. or NO., followed by a short reason."""
    
    prompt = PromptTemplate.from_template(template)
    interviewer = LLMChain(prompt=prompt, llm=llm, verbose=True)
    evaluation = interviewer.run({"answer": answer, "correct_answers": correct_answers})
    print(f"evaluation: {evaluation}")
    evaluation = evaluation.split('.')[0]

    results_dict["total"] += 1
    if evaluation.lower() == "yes":
        results_dict["success"] += 1
    else:
        results_dict["failure"] += 1

    return results_dict
