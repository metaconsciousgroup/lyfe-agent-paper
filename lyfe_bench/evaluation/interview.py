from typing import Callable, Dict, List

Agent = Callable[[Dict[str, str]], Dict[str, str]]
Judge = Callable[[str, str], bool]
Extractor = Callable[[str, str, str, Dict], List[str]]


def interview(agent: Agent, question: str):
    """
    Interview an agent with a question and get the answer.
    Input:
    - agent, question
    Output: the agent's response
    """
    action_output = agent({"interview": question, "time": "0"}) # TODO: remove time
    response = action_output.get("interview", "")
    return response

def judge_response(question: str, answer: str, response: str, judge: Judge):
    """
    Judge whether the agent's interview response matches the answer.
    Input:
    - question, answer, response
    Output: whether the judge deems that the agent's interview response matches the answer
    """
    correctness = judge(question, answer, response)
    count = 1 if correctness else 0
    return count

def extract_content(question: str, response: str, template: str, format: Dict[str, str], extractor: Extractor):
    """
    Extract content from the agent's response.
    Input:
    - question: The reference question
    - response: The response to be extracted from
    - template: The template to be used to generate a prompt, passed to the LLM for extraction
    - format: The format of the output, where the keys correspond to the expected keys and the values correspond to the description of each key
    - extractor: The function that extracts the content
    Output: the extracted content
    """
    content = extractor(
        question=question,
        response=response,
        template=template,
        format=format,
    )
    return content