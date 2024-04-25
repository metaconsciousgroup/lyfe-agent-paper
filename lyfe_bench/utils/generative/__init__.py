from omegaconf import DictConfig
from generative.generate_agents import generate_demographics, generate_background_stories, generate_agent_layout
from generative.generate_utils import get_resource_embeddings
from generative.generate_environment import generate_environment_layout
from generative.generate_tokenizer import generate_tokenizer
import agent.langmodel as langmodel


def generate(cfg: DictConfig):
    """Generate things, environments, agents, stories, etc."""
    cfg_generative = cfg.generative
    lm = langmodel.get_langmodel(cfg.langmodel)

    # Get resource embeddings from Unity
    if ('environment' in cfg_generative) and ('agents' in cfg_generative):
        get_resource_embeddings(redo=False)

    # First generate environment
    if 'environment' in cfg_generative and cfg_generative.environment.enabled:
        generate_environment_layout(cfg_generative.environment)

    # Then generate agents in the environment
    if 'agents' in cfg_generative and cfg_generative.agents.enabled:
        if 'demographics' in cfg_generative.agents:
            generate_demographics(cfg=cfg_generative.agents.demographics, lm=lm)
        if 'stories' in cfg_generative.agents:
            generate_background_stories(cfg=cfg_generative.agents.stories, lm=lm)

    # Post-processing
    # Generate tokenizer
    # if ('environment' in cfg_generative) and ('agents' in cfg_generative):
    if True:
        # TEMPORARY CONDITION
        generate_tokenizer(cfg_environment=cfg_generative.environment,
                           cfg_agents=cfg_generative.agents)
        if cfg_generative.environment.enabled:
            generate_agent_layout(cfg_generative.environment, cfg_generative.agents)
