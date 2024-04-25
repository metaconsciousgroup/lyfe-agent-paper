from typing import List, Tuple

from lyfe_agent.utils.name_utils import name_match
from lyfe_agent.base import BaseState


class ContactManager(BaseState):
    """A class that manages contacts.

    args:
        name: the name of the agent (str)
    """

    def __init__(
        self,
        name: str,
        add_self: bool = False,
        add_agents: bool = False,
        add_players: bool = False,
    ):
        self._name = name

        self._add_self = add_self
        self._add_agents = add_agents
        self._add_players = add_players

        # Agents are typically only added once
        self._agents_added = False

        self._agent_contacts = list()
        self._player_contacts = list()

    def get_match(self, name: str) -> Tuple[bool, str]:
        is_match, name = name_match(name, self.get_contacts())
        return is_match, name

    def get_contacts(self):
        return self.get_agent_contacts() + self.get_player_contacts()

    def get_agent_contacts(self):
        return list(self._agent_contacts)

    def get_player_contacts(self):
        return list(self._player_contacts)

    def add_agent_contacts(self, contacts: List[str]):
        """Add agent contacts to the agent.

        args:
            contacts: a list of contacts (str)
        """
        for contact in contacts:
            if contact not in self._agent_contacts and contact != self._name:
                self._agent_contacts.append(contact)

    def add_player_contacts(self, contacts: List[str]):
        """Add player contacts to the agent.

        args:
            contacts: a list of contacts (str)
        """
        for contact in contacts:
            if contact not in self._player_contacts:
                self._player_contacts.append(contact)

    def update(self, contacts_info):
        if contacts_info and self._add_players:
            self.add_player_contacts(contacts_info.get("player_usernames", []))

        if contacts_info and self._add_agents and (not self._agents_added):
            self.add_agent_contacts(contacts_info.get("agent_usernames", []))
            self._agents_added = True
