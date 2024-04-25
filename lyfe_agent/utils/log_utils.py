import traceback


def log_message(agent_name, event_type, message, current_time=None, wildcard=None):
    """
    This function generates a standardized log message string.

    Parameters:
    agent_name (str): The name of the agent generating the log message.
    event_type (str): The type of event being logged, such as 'INFO', 'ERROR', etc.
    message (str): The main body of the log message.
    current_time (str, optional): The time when the event occurred. Defaults to 'NA' if not provided.
    wildcard (str, optional): A wildcard field that can contain any additional information. Defaults to 'NA' if not provided.

    Returns:
    str: A formatted log message string with the structure '[agent_name][event_type][current_time][wildcard] message'.

    Example:
    >>> log_message('Agent1', 'INFO', 'This is a log message', '12:00', 'Additional info')
    '[Agent1][INFO][12:00][Additional info] This is a log message'
    """
    # set to 'NA' if no information is provided
    current_time = current_time or "NA"
    wildcard = wildcard or "NA"
    log_line = f"[{agent_name}][{event_type}][{current_time}][{wildcard}] {message}"

    return log_line


def log_error(self, error_msg, exc=None):
    """Logs the error messages."""
    if exc:
        tb_str = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
        return f"[{self.name}] {error_msg}: {exc}\n{tb_str}"
    else:
        return f"[{self.name}] {error_msg}"


def concatenate_files(start_path, target_filename, output_filename):
    """helptool for concatenate all "llm_response_data.txt" files acorss all hydra folders to one file"""
    files_to_concatenate = []

    # Walk through the directory to find the files
    for dirpath, _, filenames in os.walk(start_path):
        for filename in filenames:
            if filename == target_filename:
                files_to_concatenate.append(os.path.join(dirpath, filename))

    # Concatenate the contents of all found files
    with open(output_filename, "w") as output_file:
        for file_path in files_to_concatenate:
            with open(file_path, "r") as input_file:
                content = input_file.read()
                output_file.write(content + "\n")  # Add a newline for separation

# For logger: colorful debugging
_TEXT_COLOR_MAPPING = {
    "blue": "36;1",
    "yellow": "33;1",
    "pink": "38;5;200",
    "green": "32;1",
    "red": "31;1",
}


def get_colored_text(text: str, color: str) -> str:
    """Get colored text."""
    color_str = _TEXT_COLOR_MAPPING[color]
    return f"\u001b[{color_str}m\033[1;3m{text}\u001b[0m"
