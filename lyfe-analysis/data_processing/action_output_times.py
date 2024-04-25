import pickle

# The main issue right now is that it does not parse conversations that the user is involved in
def action_output_times(chain_data):
    chain_data = chain_data.copy()
    agent_data = {}

    # want chain data sorted by time
    chain_data.sort(key=lambda x: x["input"]["realworld_datetime"])
    # chain_data["timestamp"] = convo_data["timestamp"].apply(lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M:%S,%f"))

    for entry in chain_data:
        name = entry["input"]["name"]
        if name not in agent_data.keys():
            agent_data[name] = []
        active_func = entry["input"]["active_func"]
        timestamp = entry["input"]["realworld_datetime"]
        # end conversation if agent chooses an action other than talk
        response = entry["output"].get("response")
        agent_data[name].append((active_func, response, timestamp))

    return agent_data
 