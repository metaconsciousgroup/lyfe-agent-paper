import json
import asyncio

# These function will return coroutine objects
def run_chain_sync(chain, transition_input):
    answer = chain.run(transition_input)
    return json.loads(answer)

async def run_chain_async(chain, transition_input):
    answer = await chain.arun(transition_input)
    return json.loads(answer)

async def common_logic(runner, **kwargs):
    event_data = kwargs["event_data"]
    chain_data = kwargs["chain_data"]
    chain_manager = kwargs["chain_manager"]
    
    count = 0
    num_events = 0

    for event_info in event_data.values():
        event_num = event_info["event_num"]
        transition = chain_data["talk"][event_num]
        transition_input = transition["input"]
        transition_output = transition["output"]

        assert "talk" in chain_manager.chains.keys(), "talk chain not found"
        chain = chain_manager.chains["talk"]

        # Now, we await the coroutine object
        answer = await asyncio.coroutine(runner)(chain, transition_input) 
        
        count += answer["next_action"] == transition_output["next_action"]
        num_events += 1

    return {
        "score": count/num_events,
        "num_events": num_events
    }

def compare_next_action(**kwargs):
    # Since we made common_logic async, we need to run it in event loop
    return asyncio.run(common_logic(run_chain_sync, **kwargs))

async def async_compare_next_action(**kwargs):
    return await common_logic(run_chain_async, **kwargs)