"""Main Agent Class."""
import logging

from threading import Lock
from concurrent.futures import Executor, ThreadPoolExecutor
from typing import Dict
from hydra.utils import instantiate  # to get llm
from omegaconf import DictConfig

from lyfe_agent.brain_configs import brain_configs
from lyfe_agent.brain_utils import (
    create_interaction,
    create_state,
)
from lyfe_agent.schedule import Schedule
from lyfe_agent.states.agent_state import AgentState
from lyfe_agent.states.knowledge_manager import KnowledgeManager
from lyfe_agent.memory.memory_manager.skill_manager import SkillManager
from lyfe_agent.states.options import Options
from lyfe_agent.interactions.action_selection import ActionSelection
from lyfe_agent.interactions.cognitive_controller import CognitiveController
from lyfe_agent.interactions.option_executor import CodeOptionExecutor
from lyfe_agent.interactions.llm_call import LLMCall

logger = logging.getLogger(__name__)


class Agent:

    brain_configs: Dict[str, DictConfig] = brain_configs

    def __init__(
        self,
        id: str,
        agent_cfg: DictConfig, # Define all the inputs here
        brain_cfg: DictConfig = {}, # To be deprecated
        env_dict: Dict[str, str] = None,
        encoders=None,
        executor: Executor = None,
        memory_bank=None,
        # legacy=False,
    ):
        """Initialize an agent.

        Args:
            id: int, the id must be unique and fixed during the agent's lifetime
            agent_cfg: agent configs, memory content, etc.
                Requires the following fields:
                    - name: str
                    - brain: str or DictConfig
                    - personality: str
                    - init_goal: str
                    - memory: dict
                        - workmem: List[str]
                        - recentmem: List[str]
                        - convomem: List[str]
                        - longmem: List[str]

            brain_cfg: config for the agent's brain. To be deprecated (specified in agent_cfg)
        """
        self._id = id

        self.executor = (
            executor if executor is not None else ThreadPoolExecutor(max_workers=3)
        )
        self.encoders = encoders

        if hasattr(agent_cfg, "name") and agent_cfg.name:
            self.name = agent_cfg.name
        else:
            self.name = ''
            logger.warn("Agent name not specified. Using empty string as name.")
        self.name_tokens = self.name.split(" ")


        if brain_cfg is not None and brain_cfg != {}:
            logger.warn("brain_cfg is deprecated. Please specify brain_cfg in agent_cfg.brain")
            brain_cfg = {}

        if isinstance(agent_cfg.brain, str):
            brain_cfg = self.brain_configs[agent_cfg.brain]
        else:
            assert isinstance(agent_cfg.brain, DictConfig), "brain_cfg must be a string or a DictConfig"
            brain_cfg = agent_cfg.brain

        if hasattr(agent_cfg, "personality"):
            self.personality = agent_cfg.personality
        else:
            self.personality = "default"
            logger.warn("Agent personality not specified. Using default personality.")

        # set initial goal (may want to change)
        # TODO: current_goal is going to be deprecated soon, whose functionality will be replaced by self.current_option["option_goal"]
        self.current_goal = agent_cfg.get(
            "initial_goal", "I don't know my current goal yet."
        )

        assert env_dict is not None, "env_dict must be provided"
        self.nonce = env_dict.get("NONCE", [])

        # due to the limitation of the current implementation, the agent don't add repeated vision to memory
        self.last_vision = None

        # states and interactions setup
        self.setup_brain(
            brain_cfg, agent_cfg, encoders=self.encoders, memory_bank=memory_bank,
            env_dict=env_dict
        )

        self.lock = Lock()

    def get_active_variables(self):
        """Return a list of active variables."""
        return self.option_status.get_active_variables()

    def __getstate__(self):
        """Return a dictionary that represents the agent's state.
        For the purpose of pickling.
        """
        state = self.__dict__.copy()  # get a dictionary with the agent's attributes

        return state

    def __setstate__(self, state):
        """Set the agent's state from the given dictionary.
        For the purpose of unpickling.
        """
        self.__dict__.update(state)

    def get_executor(self):
        return self.executor

    def setup_brain(self, brain_cfg, agent_cfg, encoders, memory_bank=None, env_dict=None):
        # TODO (Robert) Fix these instantiate calls.
        # Assuming LangChain style _target_
        self.llm_type = brain_cfg.langmodel._target_.split(".")[-1]
        self.llm = instantiate(brain_cfg.langmodel)()

        # memory
        self.memory = instantiate(brain_cfg.memory)(
            llm=self.llm,
            name=self.name,
            encoders=encoders,
            executor=self.executor,
            # memory_bank=memory_bank,
            env_dict=env_dict,
        )  # This line may be slow
        
        # TODO: Figure out why OmegaConf doesn't return default values
        # TODO: TEMP
        memory_cfg = agent_cfg.get("memory", {})
        if memory_cfg is None:
            memory_cfg = {}
        if "workmem" not in memory_cfg or memory_cfg["workmem"] is None:
            memory_cfg["workmem"] = []
        memory_cfg["workmem"].append(
            agent_cfg.get("initial_goal", "I don't know my current goal yet.")
        )
        self.memory.fill_memories(memory_cfg)  # This line may be slow

        # set aliases
        for key in self.memory.memory_keys:
            setattr(self, key, getattr(self.memory, key))

        # Collects all the agent's chain input and output data
        self.data_collectors = {
            "slow_forward": [],
            "update_world_model": [],
            "memory_input_collector": [],
        }
        self.evaluation_monitor = False  # Need to think of a more general name

        # states below that need to be made part of the config
        self.schedule = Schedule(agent_cfg.get("initial_schedule", None))
        self.knowledge = KnowledgeManager(brain_cfg, agent_cfg)

        # create states
        # temporary, until all state operations are moved
        states = {}
        for state_name, state_cfg in brain_cfg.components.items():
            if state_name not in ["options", "option_status"]:
                setattr(self, state_name, create_state(self, state_name, state_cfg))
                states[state_name] = getattr(self, state_name)

        # get skills
        self.skill_manager = SkillManager(
            name=self.name,
            encoder=self.encoders.models["openai"],
            env_dict=env_dict,
            executor=self.executor,
            init_query=self.memory.latest
        )

        states["skill_manager"] = self.skill_manager

        # option manager
        self.options = Options(
            name=self.name,
            nearby_creature=self.nearby_creature,
            observable_entities=self.observable_entities,
            current_option=self.current_option,
            option_history=self.option_history,
            skill_manager=self.skill_manager,
            **brain_cfg.options
        )

        self.agent_state = AgentState(
            agent=self,
            memory=self.memory,
            options=self.options,
            **states,
            **brain_cfg.agent_state
        )

        self.llm_call = LLMCall(
            name=self.name,
            llm=self.llm,
            memory=self.memory,
            agent_state=self.agent_state,
            chains=brain_cfg.chains,
        )

        # create interactions
        for interaction_name, interaction_cfg in brain_cfg.interactions.items():
            setattr(
                self,
                interaction_name,
                create_interaction(self, interaction_name, interaction_cfg, self.nonce),
            )

        self.option_executor = {}
        for name, cfg in brain_cfg.option_executor.items():
            self.option_executor[name] = create_interaction(self, name, cfg, self.nonce)
        
        # TODO: Temporary, until we integrate skill manager into options
        # TODO: Also should have only one option executor for skill, not one for each skill
        for skill in self.skill_manager.skills:
            self.option_executor[skill["key"]] = CodeOptionExecutor(
                name=skill["key"],
                description=skill["description"],
                code=skill["code"],
                docstring=skill["docstring"],
                llm=self.llm,
                sources={
                    # "current_option": self.current_option,
                    "agent_state": self.agent_state,
                    "options": self.options,
                }
            )

        self.cognitive_controller = CognitiveController(
            name=self.name,
            chain=brain_cfg.chains.cognitive_controller,
            llm=self.llm,
            memory=self.memory,
            data_collector=self.data_collectors["slow_forward"], # TODO: Need better data collector structure
            executor=self.executor,
        )

        self.action_selection = ActionSelection(
            agent_state = self.agent_state,
            name = self.name,
            memory = self.memory,
            data_collectors = self.data_collectors,
            executor = self.executor,
            option_executor = self.option_executor,
        )

    def __call__(self, observations, **kwargs):
        """Main call function of the agent."""
        try:
            # Process observations to obtain inputs to state
            sense_natural_language = self.sense_interaction.execute(observations)
            self.encode_talk.execute(observations)

            # State updates
            self.agent_state.update(observations)

            self.memory.add(
                content=sense_natural_language,
                data_collector=self.data_collectors["memory_input_collector"],
            )

            # TODO: for ablation test
            self.memory.update(
                new_summary=self.summary_state.data,
            )

            # Process world model thread
            self.summary_interaction.execute(sense_natural_language)

            # Cognitive controller thread
            self.cognitive_controller.execute(observations, self.agent_state)

            # may want this to just modify a state, then return state
            action_to_env = self.action_selection.execute(observations)

            # post process to include observables
            action_to_env |= self.agent_state.expressions

        except Exception as e:
            import traceback

            stack_trace = traceback.format_exc()
            logger.error(
                f"[AGENT] Error in agent {self.name}: {e}\nStack Trace:\n{stack_trace}\nobservations: {observations}]"
            )
            raise e
        
        # Hacky way to support agent looking at another character.
        if observations.get("talk_structured", None) is not None:
            character_id = observations["talk_structured"].get("character_id", None)
            if character_id is not None:
                action_to_env["look_at"] = character_id
                message = observations["talk_structured"]["message"]
                for token in self.name_tokens:
                    if token.lower() in message.lower():
                        action_to_env["stop_moving"] = True
                        break

        return action_to_env

    @property
    def id(self):
        return self._id