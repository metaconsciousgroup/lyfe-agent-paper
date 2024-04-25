class BaseState:
    def __init__(self, input_keys):
        self.value = None

    def update(self, input_dict):
        pass


class BaseInteraction:
    expected_inputs = []
    def __init__(self, sources, targets):
        assert set(self.expected_inputs) <= set(list(sources.keys())), "Missing source inputs"
        for source_name, source_obj in sources.items():
            setattr(self, source_name, source_obj)
        self.targets = targets

    def execute(self):
        """Do something that takes some time"""
        input_to_state = None
        return input_to_state