from collections import deque
from typing import List, Optional

"""Systems for handling information passing within the environment between agents."""

class MessagingSystem:
    def __init__(self):
        """
        Initializes a new MessagingSystem instance with an empty message dictionary.
        """
        self.messages = {}

    def send_message(self, sender, receiver, message):
        """
        Sends a message from the sender to the receiver.

        Args:
            sender (str): The username of the sender.
            receiver (str): The username of the receiver.
            message (Any): The message to send.
        """
        if receiver not in self.messages:
            self.messages[receiver] = []

        self.messages[receiver].append((sender, message))

    def receive_messages(self, receiver):
        """
        Retrieves all messages sent to the receiver and removes them from the system.

        Args:
            receiver (str): The username of the receiver.

        Returns:
            list: A list of tuples containing the sender and message for each message.
        """
        if receiver not in self.messages:
            return []

        messages = self.messages[receiver]
        del self.messages[receiver]

        return messages

class TalkSystem:
    def __init__(self):
        """
        Initializes a new MessagingSystem instance with an empty message dictionary.
        """
        self.messages = {}

    def send_message(self, sender, receiver, message):
        """
        Sends a message from the sender to the receiver.

        Args:
            sender (str): The username of the sender.
            receiver (str): The username of the receiver.
            message (Any): The message to send.
        """
        if receiver not in self.messages:
            self.messages[receiver] = deque()

        self.messages[receiver].append((sender, message))

    def receive_messages(self, receiver):
        """
        Retrieves the oldest message sent to the receiver and removes it from the system.

        Args:
            receiver (str): The username of the receiver.

        Returns:
            tuple: A tuple containing the sender and message.
        """
        if receiver not in self.messages or not self.messages[receiver]:
            return None

        message = self.messages[receiver].popleft()

        # If the deque becomes empty after popping, we can delete the key from the dictionary
        if not self.messages[receiver]:
            del self.messages[receiver]

        return message