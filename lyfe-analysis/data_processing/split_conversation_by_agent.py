import re

from lyfe_agent.utils.name_utils import name_match
from datetime import datetime

class ConversationItem:
    def __init__(self, response, agent):
        self.response = response
        self.agent = agent
    
    def __str__(self):
        return f"{self.agent}: {self.response}"
    
    def __repr__(self):
        return str(self)
    
    def __eq__(self, other):
        return self.response == other.response and self.agent == other.agent
    
class Conversation:
    def __init__(self):
        self.conversation_list = []
    
    def append(self, convo_item):
        self.conversation_list.append(convo_item)
    
    def __str__(self):
        return "\n".join([str(i) for i in self.conversation_list])
    
    def __repr__(self):
        return str(self)
    
    def __getitem__(self, index):
        if isinstance(index, slice):
            return self.conversation_list[index.start:index.stop:index.step]
        return self.conversation_list[index]
    
    def __len__(self):
        return len(self.conversation_list)
    
    def __add__(self, other):
        return Conversation(self.conversation_list + other.conversation_list)
    
    def is_empty(self):
        return len(self.conversation_list) == 0

def get_speaker_and_response(input_str):
    """
    Parses a string containing a pattern of "<name> said: <message>" and extracts the name and message.

    Args:
    - input_str (str): A string containing the pattern "<name> said: <message>".

    Returns:
    - list: A list containing two elements: the name of the speaker and the message. 
            If the input string doesn't match the pattern, an empty list is returned.
    """
    
    pattern = r"(.+?) said: (.+)"
    match = re.match(pattern, input_str)
    if not match:
        return None
    return [match.group(1), match.group(2)]
    

def split_text_to_convo_items(convomem):
    """
    Splits a string containing a conversation into a list of ConversationItem objects.
    """
    item_list = convomem.split("\n")
    convo_items = []
    for item in item_list:
        output = get_speaker_and_response(item)
        if output:
            speaker, response = output
            convo_items.append(ConversationItem(response=response, agent=speaker))
    return convo_items

# temporary name_match

def differ_by_one(s1, s2):
    """
    Returns True if strings s1 and s2 differ by exactly one character,
    otherwise returns False.
    """
    if len(s1) != len(s2):
        return False

    differences = 0
    for char1, char2 in zip(s1, s2):
        if char1 != char2:
            differences += 1
        if differences > 1:
            return False

    return differences <= 1


# The main issue right now is that it does not parse conversations that the user is involved in
def split_conversation_by_agent(chain_data, convo_data):
    chain_data = chain_data.copy()
    agent_convos = {}

    # def convert_to_datetime(event):
    #     event["input"]["event_time"] = datetime.strptime(event["input"]["output_time"], "%Y-%m-%d %H:%M:%S.%f")
    #     return event

    # # want chain data sorted by time
    # chain_data = list(map(convert_to_datetime, chain_data))
    # chain_data.sort(key=lambda x: x["input"]["event_time"])

    # # print(chain_data[0]["input"]["event_time"])
    # # print(convo_data["timestamp"])
    # convo_data["timestamp"] = convo_data["timestamp"].apply(lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M:%S,%f"))

    # for item in chain_data:
    #     if item["input"]["active_func"] == "talk":
    #         print("(", item["input"]["event_time"], ") " , item["input"]["name"] + ": ", item["output"]["response"])
    # print(convo_data)

    # want chain data sorted by time
    chain_data.sort(key=lambda x: x["input"]["current_time"])
    convo_data["timestamp"] = convo_data["timestamp"].apply(lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M:%S,%f"))

    for item in chain_data:
        if item["input"]["active_func"] == "talk":
            print("(", item["input"]["current_time"], ") " , item["input"]["name"] + ": ", item["output"]["response"])
    print(convo_data)



    # sometimes, nearby creature names are different from names (e.g. hyphens), so create a dictionary to get the mapping
    # get nearby creature names
    names = []
    nearby_creature_names = []
    for entry in chain_data:
        nearby_creature = entry["input"]["nearby_creature"]
        nearby_creature = nearby_creature.split(', ') if nearby_creature != '' else []
        nearby_creature_names += nearby_creature
        nearby_creature_names = list(set(nearby_creature_names))

        names.append(entry["input"]["name"])
        names = list(set(names))
    names_mapping = {}
    for nearby_creature_name in nearby_creature_names:
        for name in names:
            # if name_match(name, nearby_creature_name):
            if differ_by_one(name, nearby_creature_name):
                print("NAME MATCH: ", name, nearby_creature_name)
                names_mapping[nearby_creature_name] = name

    i = 0
    for entry in chain_data:
        self_name = entry["input"]["name"]
        active_func = entry["input"]["active_func"]
        # end conversation if agent chooses an action other than talk
        if active_func != "talk":
            # if the latest conversation is empty, don't add a new one
            if self_name not in agent_convos.keys():
                agent_convos[self_name] = [Conversation()]
            elif not agent_convos[self_name][-1].is_empty():
                agent_convos[self_name].append(Conversation())
        
        else:
            response = entry["output"].get("response")
            convo_item = ConversationItem(response, self_name)

            # nearby_creature = names_mapping[entry["input"]["nearby_creature"]]
            # nearby_creature = [] if nearby_creature == '' else nearby_creature.split(', ')
            nearby_creature = entry["input"]["nearby_creature"]
            nearby_creature = [] if nearby_creature == '' else nearby_creature.split(', ')
            # nearby_creature = [names_mapping[name] for name in nearby_creature]

            # # get recent convo items from convo mem to get user responses (from most recent to least recent)
            # recent_convo_items = split_text_to_convo_items(entry["input"]["convomem"])
            # # from most recent to least recent
            # recent_convo_items.reverse()

            for name in [self_name] + nearby_creature:
                # initialize conversation records for agent if it doesn't exist
                if name not in agent_convos.keys():
                    agent_convos[name] = [Conversation()]
                # # if conversation records exist, add any recent convo items to the latest conversation that involve the user
                # else:
                #     for convo_item in recent_convo_items:
                #         if convo_item.agent in names:

                #     for convo_item in recent_convo_items:
                #         if convo_item.agent not in names:
                # if name != self_name:
                #     print("HEY YA: ", self_name, name)
                #     if name == "Francesco Bianchi":
                #         print(agent_convos[self_name][-1])
                agent_convos[name][-1].append(convo_item)

    # print(agent_convos["Aaliyah Williams"])

    print(names_mapping)

    return agent_convos
 