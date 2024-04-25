import pandas as pd
from textwrap import wrap


# The main issue right now is that it does not parse conversations that the user is involved in
def user_ref_by_agent(chain_data, user_names):
    chain_data = chain_data.copy()

    # want chain data sorted by time
    chain_data.sort(key=lambda x: x["input"]["current_time"])

    valid_entries = []

    # get valid entries
    for entry in chain_data:
        if entry["input"]["active_func"] == "talk":
            nearby_creature = entry["input"]["nearby_creature"]
            nearby_creature = nearby_creature.split(', ') if nearby_creature != '' else []

            response = entry["output"].get("response")
            
            # check if user name is in response
            is_user_in_response = any([name in response for name in user_names])

            if is_user_in_response:
                # check if user name is in nearby creature
                is_user_in_nearby_creature = any([any([name in nearby_name for nearby_name in nearby_creature]) for name in user_names])
                if not is_user_in_nearby_creature and nearby_creature != []:
                    valid_entries.append(entry)

    # extract only conversation and nearby_creatures
    def extract_response_and_nearby_creatures(entry):
        name = entry["input"]["name"]
        response = entry["output"]["response"]
        nearby_creature = entry["input"]["nearby_creature"]
        nearby_creature = nearby_creature.split(', ') if nearby_creature != '' else []
        return {"name": name, "response": response, "nearby_creature": nearby_creature}

    df = pd.DataFrame([extract_response_and_nearby_creatures(entry) for entry in valid_entries])

    # print
    def print_table(data):
        # Maximum width for the quotes column
        max_quote_width = 60
        
        # Determine the maximum width for the nearby column
        max_nearby_width = max(len(str(item)) for item in data['nearby_creature'])
        
        # Print header
        print(f'{"Quotes":<{max_quote_width}} | {"Nearby":<{max_nearby_width}}')
        print('-' * (max_quote_width + max_nearby_width + 3))

        # Iterate over the data
        for name, response, nearby in zip(data['name'], data['response'], data['nearby_creature']):
            quote = f"{name}: {response}"
            nearby = ", ".join(nearby) if nearby != [] else ""
            # Wrap the quote text
            wrapped_quote = wrap(quote, width=max_quote_width)
            
            # Print the rows
            for i, line in enumerate(wrapped_quote):
                if i == 0:
                    print(f'{line:<{max_quote_width}} | {nearby:<{max_nearby_width}}')
                else:
                    print(f'{line:<{max_quote_width}} |')
            print('-' * (max_quote_width + max_nearby_width + 3))
    
    print_table(df)

    return df

 