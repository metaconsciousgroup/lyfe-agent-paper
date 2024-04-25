import re

from datetime import datetime

# The main issue right now is that it does not parse conversations that the user is involved in
def get_convo_items(convo_data):
    convo_data["timestamp"] = convo_data["timestamp"].apply(lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M:%S,%f"))
    return convo_data
 