class Tool:
    """
    This is the base tool class. All tools consist of an `update` method that takes in observations and updates the tool.
    The other requirement is that the class attribute `available_actions` is a list of strings that describe the actions that the tool can take.
    For each element in `available_actions`, there should be a method with the same name that takes in the arguments for the action.
    """
    available_actions = []

    def __init__(self) -> None:
        pass

    def update(self, observations):
        pass