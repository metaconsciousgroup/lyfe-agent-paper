import numpy as np


def string_to_ascii(text, max_len=100):
    # Handle None input
    if text is None:
        return np.zeros(max_len, dtype=np.uint8)
    text = text.encode("ascii", "ignore").decode()

    ascii_values = np.zeros(max_len, dtype=np.uint8)
    for i, char in enumerate(text):
        if i >= max_len:
            break
        ascii_values[i] = ord(char)

    return ascii_values


def ascii_to_string(observation):
    """Convert the ascii to string."""
    # Handle None input
    if observation is None:
        return ""

    # Convert list to numpy array if necessary
    if isinstance(observation, list):
        observation = np.array(observation, dtype=np.uint8)

    # Find the end of string index
    end_of_string_index = np.where(observation == 0)[0]

    # If no zero padding found, convert entire observation
    end_of_string_index = end_of_string_index[0] if end_of_string_index.size > 0 else len(observation)
    int_observations = observation[:end_of_string_index]

    # Use NumPy to convert to characters and then to string
    char_observations = np.array([chr(i) for i in int_observations])
    string_observations = ''.join(char_observations)

    return string_observations
