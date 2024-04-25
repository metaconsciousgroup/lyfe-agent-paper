import json
import asyncio
from langchain import PromptTemplate, LLMChain

from evaluation.utils.manage_content import extract_recent_content

# Common logic for both synchronous and asynchronous versions
async def common_check_response(runner, **kwargs):
    event_data = kwargs["event_data"]
    chain_data = kwargs["chain_data"]
    llm = kwargs["llm"]
    chain_manager = kwargs["chain_manager"]
    
    # Setup evaluator chain
    template = """Consider the following question: ```{question}```
            Consider the following answer to the question, delimited by triple backticks: \n```\n-{answer}\n```
            Determine whether this answer contains the idea from ANY of the following sentences (importantly, wording does NOT have to be the same): \n-{correct_answers}
            You should answer YES if the information is contained in any of the sentences, even if the wording is different.
            Your answer should be a one-word response, YES. or NO., followed by a short reason."""
    prompt = PromptTemplate.from_template(template)
    evaluator = LLMChain(prompt=prompt, llm=llm, verbose=True)
    
    count = 0
    num_events = 0

    # Iterate through specified entries
    for event_info in event_data.values():
        event_num = event_info["event_num"]
        transition = chain_data["talk"][event_num]
        transition_input = transition["input"]
        question = extract_recent_content(transition_input["convomem"])
        print("question: ", question)
        
        correct_answers = event_info.answers
        correct_answers = correct_answers if isinstance(correct_answers, str) else '\n-'.join(list(correct_answers))
        print("correct answers: ", correct_answers)
        
        # Need to get talk chain
        assert "talk" in chain_manager.chains.keys(), "talk chain not found"
        chain = chain_manager.chains["talk"]
        
        # Runner function takes care of running the chain
        result = runner(chain, transition_input)
        # answer = await runner(chain, transition_input)
        if asyncio.iscoroutine(result):
            answer = await result
        else:
            answer = result
        answer = json.loads(answer)["response"]

        # evaluate answer
        evaluation = evaluator.run({"question": question, "answer": answer, "correct_answers": correct_answers})
        print("evaluation: ", evaluation, "\n")

        # process answer
        evaluation = evaluation.split('.')[0]

        num_events += 1
        count += evaluation.lower() == "yes"
 
    return {
        "score": count/num_events,
        "num_events": num_events
    }

# Synchronous runner
def run_chain_sync(chain, transition_input):
    return chain.run(transition_input)

# Asynchronous runner
async def run_chain_async(chain, transition_input):
    return await chain.arun(transition_input)

# Synchronous version
def check_response(**kwargs):
    return asyncio.run(common_check_response(run_chain_sync, **kwargs))

# Asynchronous version
async def async_check_response(**kwargs):
    return await common_check_response(run_chain_async, **kwargs)



# import json
# from langchain import PromptTemplate, LLMChain

# from evaluation.utils.manage_content import extract_recent_content

# def check_response(**kwargs):
#     event_data = kwargs["event_data"]
#     chain_data = kwargs["chain_data"]
#     llm = kwargs["llm"]
#     chain_manager = kwargs["chain_manager"]

#     # setup evaluator chain
#     template = """Consider the following question: ```{question}```
#             Consider the following answer to the question, delimited by triple backticks: \n```\n-{answer}\n```
#             Determine whether this answer contains the idea from ANY of the following sentences (importantly, wording does NOT have to be the same): \n-{correct_answers}
#             You should answer YES if the information is contained in any of the sentences, even if the wording is different.
#             Your answer should be a one-word response, YES. or NO., followed by a short reason."""
    
#     prompt = PromptTemplate.from_template(template)
#     evaluator  = LLMChain(prompt=prompt, llm=llm, verbose=True)
    
#     # counters
#     count = 0
#     num_events = 0

#     # Iterate through specified entries
#     for event_info in event_data.values():
#         event_num = event_info["event_num"]
#         transition = chain_data["talk"][event_num]
#         transition_input = transition["input"]
#         question = extract_recent_content(transition_input["convomem"])
#         print("question: ", question)
        
#         correct_answers = event_info.answers
#         correct_answers = correct_answers if isinstance(correct_answers, str) else '\n-'.join(list(correct_answers))
#         print("correct answers: ", correct_answers)

#         # need to get talk chain
#         assert "talk" in chain_manager.chains.keys(), "talk chain not found"
#         chain = chain_manager.chains["talk"]
#         answer = chain.run(transition_input)
#         answer = json.loads(answer)["response"]
#         print("my answer: ", answer)

#         # evaluate answer
#         evaluation = evaluator.run({"question": question, "answer": answer, "correct_answers": correct_answers})
#         print("evaluation: ", evaluation, "\n")

#         # process answer
#         evaluation = evaluation.split('.')[0]

#         num_events += 1
#         count += evaluation.lower() == "yes"
 
#     return {
#         "score": count/num_events,
#         "num_events": num_events
#         }